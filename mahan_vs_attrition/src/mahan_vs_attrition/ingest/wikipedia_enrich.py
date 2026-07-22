"""Wikipedia enrichment: extract infobox data for wars and battles.

Rate-limited with randomized sleeps. Never hammer the API.
Saves progress incrementally so we can resume if interrupted.
"""

import json
import logging
import random
import re
import time
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import requests

logger = logging.getLogger(__name__)

USER_AGENT = (
    "MahanVsAttrition/1.0 "
    "(https://github.com/your-org/mahan_vs_attrition; research-project@example.com) "
    "Academic research project - polite scraper"
)

API_URL = "https://en.wikipedia.org/w/api.php"
MIN_SLEEP = 1.8
MAX_SLEEP = 3.5
BATCH_SLEEP_AFTER = 25
BATCH_SLEEP_DURATION = 8.0


class WikipediaClient:
    """Rate-limited client for the Wikipedia API."""

    def __init__(self, cache_dir: Path | None = None):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self._last_request = 0.0
        self._request_count = 0
        self.cache_dir = cache_dir
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)

    def _rate_limit(self):
        """Sleep a random interval to stay under rate limits."""
        elapsed = time.time() - self._last_request
        delay = random.uniform(MIN_SLEEP, MAX_SLEEP)
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._request_count += 1
        if self._request_count % BATCH_SLEEP_AFTER == 0:
            extra = random.uniform(2.0, BATCH_SLEEP_DURATION)
            logger.debug(f"Batch pause: {extra:.1f}s after {self._request_count} requests")
            time.sleep(extra)
        self._last_request = time.time()

    def _get(self, params: dict) -> dict:
        """Make a rate-limited GET request."""
        self._rate_limit()
        params["format"] = "json"
        resp = self.session.get(API_URL, params=params, timeout=30)
        if resp.status_code == 429:
            retry = int(resp.headers.get("Retry-After", 30))
            logger.warning(f"429 hit, sleeping {retry}s")
            time.sleep(retry + random.uniform(1, 5))
            return self._get(params)
        resp.raise_for_status()
        return resp.json()

    def search(self, query: str, limit: int = 3) -> list[dict]:
        """Search Wikipedia for pages matching query."""
        data = self._get({
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
        })
        return data.get("query", {}).get("search", [])

    def get_page_wikitext(self, title: str) -> str | None:
        """Get raw wikitext for a page by title."""
        data = self._get({
            "action": "parse",
            "page": title,
            "prop": "wikitext",
            "formatversion": 2,
        })
        parse = data.get("parse")
        if parse is None:
            return None
        return parse.get("wikitext", "")

    def extract_infobox(self, wikitext: str) -> dict[str, str]:
        """Extract infobox fields from wikitext.

        Handles {{Infobox military conflict}}, {{Infobox battle}}, etc.
        Returns a dict of field_name: value (cleaned). Correctly handles
        nested templates inside field values.
        """
        if not wikitext:
            return {}

        # Find the infobox start
        m = re.search(r"\{\{\s*Infobox\s+", wikitext, re.IGNORECASE)
        if not m:
            return {}

        start = m.start()

        # Find the matching closing }} using brace-depth tracking
        depth = 0
        end = start
        for i in range(start, len(wikitext)):
            if wikitext[i] == "{" and i + 1 < len(wikitext) and wikitext[i + 1] == "{":
                depth += 1
                i += 1
            elif wikitext[i] == "}" and i + 1 < len(wikitext) and wikitext[i + 1] == "}":
                depth -= 1
                i += 1
                if depth == 0:
                    end = i + 1
                    break

        infobox_text = wikitext[start:end + 1]

        # Split into top-level pipes: | that are inside the infobox
        # (depth==1) but not inside nested templates (depth >= 2)
        fields = {}
        depth = 0
        field_starts = []
        for i, ch in enumerate(infobox_text):
            if ch == "{" and i + 1 < len(infobox_text) and infobox_text[i + 1] == "{":
                depth += 1
            elif ch == "}" and i + 1 < len(infobox_text) and infobox_text[i + 1] == "}":
                depth -= 1
            elif ch == "|" and depth == 1:
                field_starts.append(i)

        # Extract each field between pipes (skip the first which is {{Infobox...)
        for fi in range(1, len(field_starts)):
            seg_start = field_starts[fi - 1] + 1
            seg_end = field_starts[fi] if fi < len(field_starts) else len(infobox_text)
            segment = infobox_text[seg_start:seg_end].strip()

            # Split on first = to get key/value
            eq_pos = segment.find("=")
            if eq_pos == -1:
                continue
            key = segment[:eq_pos].strip()
            val = segment[eq_pos + 1:].strip()

            # Clean wikitext markup: [[links]]
            val = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]", r"\1", val)
            # Remove {{templates}} but keep text between
            val = re.sub(r"\{\{[^}]*\}\}", "", val)
            # HTML tags
            val = re.sub(r"<[^>]+>", "", val)
            # Bold/italic
            val = re.sub(r"'{2,}", "", val)
            # Collapse whitespace
            val = re.sub(r"\s+", " ", val).strip()

            if val and len(val) < 500:
                if val.lower() in ("yes", "y", "true", "t"):
                    val = "yes"
                elif val.lower() in ("no", "n", "false", "f"):
                    val = "no"
                fields[key.lower()] = val

        return fields

    def find_war_article(self, war_name: str, alternate_names: list[str] | None = None) -> str | None:
        """Find the Wikipedia article for a war.

        Tries exact match, then appending 'War', then search.
        Returns the page title or None.
        """
        candidates = [war_name]
        if alternate_names:
            candidates.extend(alternate_names)
        if not war_name.lower().endswith("war"):
            candidates.append(war_name + " War")
            candidates.append(war_name + " war")
        for name in list(candidates):
            parts = name.split()
            if len(parts) > 1:
                candidates.append(" ".join(parts[:-1]) + " War")

        for title in candidates:
            data = self._get({
                "action": "query",
                "titles": title,
                "formatversion": 2,
            })
            pages = data.get("query", {}).get("pages", [])
            if pages and not pages[0].get("missing"):
                return title

        # Search
        results = self.search(war_name + " war")
        if results:
            return results[0]["title"]
        results = self.search(war_name)
        if results:
            return results[0]["title"]
        return None

    def enrich_war(self, title: str) -> dict[str, Any]:
        """Enrich a single war from its Wikipedia article."""
        wikitext = self.get_page_wikitext(title)
        if not wikitext:
            return {"title": title, "status": "not_found"}

        infobox = self.extract_infobox(wikitext)
        result = {
            "title": title,
            "status": "ok",
            "infobox": infobox,
        }

        # Map infobox fields to our schema
        mapping = {
            "result": "outcome_wikipedia",
            "date": "date_raw",
            "place": "location",
            "territory": "territorial_changes",
            "combatant1": "side_a_raw",
            "combatant2": "side_b_raw",
            "strength1": "strength_a",
            "strength2": "strength_b",
            "casualties1": "casualties_a",
            "casualties2": "casualties_b",
            "commander1": "commander_a",
            "commander2": "commander_b",
        }
        for wiki_key, our_key in mapping.items():
            if wiki_key in infobox:
                result[our_key] = infobox[wiki_key]

        # Parse result for structured outcome info
        outcome_raw = infobox.get("result", "")
        if outcome_raw:
            result["outcome_classified"] = classify_outcome(outcome_raw)

        # Parse date for structured date info
        date_raw = infobox.get("date", "")
        if date_raw:
            result["date_info"] = parse_date_from_infobox(date_raw)

        # Parse place for region hints
        place = infobox.get("place", "")
        if place:
            # Strip wikitext artifacts
            clean = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]", r"\1", place)
            result["location_clean"] = clean

        return result

    def enrich_battle(self, title: str) -> dict[str, Any]:
        """Enrich a single battle from its Wikipedia article."""
        wikitext = self.get_page_wikitext(title)
        if not wikitext:
            return {"title": title, "status": "not_found"}

        infobox = self.extract_infobox(wikitext)
        result = {
            "title": title,
            "status": "ok",
            "infobox": infobox,
        }

        mapping = {
            "result": "outcome",
            "date": "date_raw",
            "location": "location",
            "partof": "part_of",
            "strength1": "strength_a",
            "strength2": "strength_b",
            "casualties1": "casualties_a",
            "casualties2": "casualties_b",
            "commander1": "commander_a",
            "commander2": "commander_b",
        }
        for wiki_key, our_key in mapping.items():
            if wiki_key in infobox:
                result[our_key] = infobox[wiki_key]

        return result


class ProgressSaver:
    """Saves incremental progress to resume after interruption."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict:
        if self.path.exists():
            with open(self.path) as f:
                return json.load(f)
        return {
            "completed": [],
            "failed_retryable": [],
            "failed_final": [],
            "results": [],
            "errors": [],
        }

    def save(self, data: dict):
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def is_completed(self, key: str) -> bool:
        data = self.load()
        return key in data.get("completed", [])

    def is_failed_final(self, key: str) -> bool:
        data = self.load()
        return key in data.get("failed_final", [])

    def should_skip(self, key: str) -> bool:
        """Skip if completed successfully OR marked as final failure."""
        data = self.load()
        return key in data.get("completed", []) or key in data.get("failed_final", [])

    def record_result(self, key: str, result: dict):
        data = self.load()
        data["completed"].append(key)
        data["results"].append(result)
        data["failed_retryable"] = [k for k in data["failed_retryable"] if k != key]
        self.save(data)

    def record_error(self, key: str, error: str, final: bool = False):
        data = self.load()
        data["errors"].append({"key": key, "error": error, "final": final})
        if final:
            if key not in data["failed_final"]:
                data["failed_final"].append(key)
            data["failed_retryable"] = [k for k in data["failed_retryable"] if k != key]
        else:
            if key not in data["failed_retryable"]:
                data["failed_retryable"].append(key)
        self.save(data)


# ---------------------------------------------------------------------------
# Domain-specific enrichment functions
# ---------------------------------------------------------------------------

OUTCOME_MAP = {
    "decisive victory": "decisive",
    "victory": "win",
    "defeat": "loss",
    "decisive defeat": "decisive_loss",
    "inconclusive": "stalemate",
    "ceasefire": "ceasefire",
    "armistice": "armistice",
    "treaty": "treaty",
    "surrender": "surrender",
}


def classify_outcome(result_str: str) -> dict:
    """Classify an outcome string into structured fields."""
    if not result_str:
        return {}
    rl = result_str.lower()
    outcome_class = None
    is_decisive = False
    has_treaty = False
    has_armistice = False
    has_surrender = False

    # Check compound terms first, then single terms
    for key in sorted(OUTCOME_MAP, key=len, reverse=True):
        if key in rl:
            outcome_class = OUTCOME_MAP[key]
            break
    if "decisive" in rl and ("victory" in rl or "defeat" in rl):
        is_decisive = True

    if "treaty" in rl or "treaty of" in rl:
        has_treaty = True
    if "armistice" in rl:
        has_armistice = True
    if "surrender" in rl:
        has_surrender = True

    # Extract winner: text before "victory" or "win"
    winner = None
    for delim in [" victory", " win"]:
        idx = rl.find(delim)
        if idx > 0:
            candidate = result_str[:idx].strip().rstrip(",")
            if candidate and "end of" not in candidate.lower() and "outbreak" not in candidate.lower():
                # Strip leading "Decisive " if present
                for prefix in ["Decisive ", "decisive "]:
                    if candidate.startswith(prefix):
                        candidate = candidate[len(prefix):].strip()
                if candidate and candidate not in ("an", "a"):
                    winner = candidate
                break

    # Extract loser: text before "defeat"
    loser = None
    for delim in [" defeat", " loss"]:
        idx = rl.find(delim)
        if idx > 0:
            candidate = result_str[:idx].strip().rstrip(",")
            if candidate and len(candidate) < 60:
                loser = candidate
                break

    result = {
        "outcome_class": outcome_class,
        "is_decisive": is_decisive,
        "has_treaty": has_treaty,
        "has_armistice": has_armistice,
        "has_surrender": has_surrender,
    }
    if winner:
        result["winner_from_outcome"] = winner
    if loser:
        result["loser_from_outcome"] = loser
    return result


def parse_date_from_infobox(date_str: str) -> dict:
    """Extract start/end dates from an infobox date field."""
    if not date_str:
        return {}
    result = {}
    if "–" in date_str:
        parts = date_str.split("–")
        result["infobox_date_start"] = parts[0].strip()
        result["infobox_date_end"] = parts[-1].strip()
    elif "-" in date_str and re.search(r"\d{4}", date_str):
        parts = date_str.split("-")
        result["infobox_date_start"] = parts[0].strip()
        result["infobox_date_end"] = parts[-1].strip()
    else:
        result["infobox_date_single"] = date_str
    return result


# ---------------------------------------------------------------------------
# Main enrichment pipeline
# ---------------------------------------------------------------------------


def enrich_all_interstate_wars(
    client: WikipediaClient,
    wars_df: pd.DataFrame,
    title_mapping: dict[str, str],
    progress_path: Path,
) -> list[dict]:
    """Enrich all interstate wars from their Wikipedia articles."""
    saver = ProgressSaver(progress_path)

    interstate = wars_df[wars_df["war_type"] == "interstate"]
    results = []
    for _, war in interstate.iterrows():
        wid = war["war_id"]
        if saver.should_skip(wid):
            continue

        source_id = war.get("source_war_id", "")
        title = title_mapping.get(source_id) or title_mapping.get(wid)
        if not title:
            # Fallback: derive from war_name via client search
            war_name = str(war.get("war_name", "") or "")
            if war_name:
                try:
                    title = client.find_war_article(war_name)
                except Exception as e:
                    logger.debug(f"find_war_article fallback failed for {wid}: {e}")
                    title = None
        if not title:
            saver.record_error(wid, "no title mapping and no fallback", final=True)
            continue

        logger.info(f"Enriching {wid} ({title})")
        try:
            data = client.enrich_war(title)
            data["war_id"] = wid
            if data.get("status") == "ok" and data.get("infobox"):
                outcome_info = classify_outcome(data.get("outcome", ""))
                data.update(outcome_info)
                date_info = parse_date_from_infobox(data.get("date_raw", ""))
                data.update(date_info)
                saver.record_result(wid, data)
                results.append(data)
            else:
                # Not found is a final failure
                saver.record_error(wid, f"not_found_or_no_infobox: title={title}", final=True)
        except Exception as e:
            logger.warning(f"Error enriching {wid}: {e}")
            # Transient errors stay retryable
            saver.record_error(wid, str(e), final=False)

    return results


def enrich_battles_for_war(
    client: WikipediaClient,
    war_id: str,
    battles_df: pd.DataFrame,
    progress_path: Path,
) -> list[dict]:
    """Enrich all battles for a given war."""
    saver = ProgressSaver(progress_path)
    war_battles = battles_df[battles_df["war_id"] == war_id]
    results = []
    for _, battle in war_battles.iterrows():
        bid = battle["battle_id"]
        bname = battle["battle_name"]
        if not bname or bname in ("", "nan"):
            continue
        if saver.should_skip(bid):
            continue

        # Map battle name to Wikipedia title: try "Battle of X" then search
        bname_clean = bname.split("(")[0].strip().rstrip("1234567890 ").strip()
        title_candidates = [
            f"Battle of {bname}",
            f"Battle of {bname_clean}",
            f"{bname} Battle",
            bname,
        ]
        title = None
        try:
            for t in title_candidates:
                data_check = client._get({
                    "action": "query",
                    "titles": t,
                    "formatversion": 2,
                })
                pages = data_check.get("query", {}).get("pages", [])
                if pages and not pages[0].get("missing"):
                    title = t
                    break
        except Exception as e:
            logger.debug(f"  Battle {bname}: API error during title search: {e}")
            saver.record_error(bid, f"title_search_error: {e}", final=False)
            continue

        if not title:
            try:
                search_results = client.search(f"{bname} battle", limit=2)
                if search_results:
                    title = search_results[0]["title"]
            except Exception as e:
                saver.record_error(bid, f"search_error: {e}", final=False)
                continue

        if not title:
            logger.debug(f"  Battle {bname}: no Wikipedia article found")
            saver.record_error(bid, f"No article found for {bname}", final=True)
            continue

        logger.info(f"  Battle: {bname} -> {title}")
        try:
            data = client.enrich_battle(title)
            data["battle_id"] = bid
            data["war_id"] = war_id
            if data.get("status") == "ok" and data.get("infobox"):
                outcome_info = classify_outcome(data.get("outcome", ""))
                data.update(outcome_info)
                saver.record_result(bid, data)
                results.append(data)
            else:
                saver.record_error(bid, f"not_found: title={title}", final=True)
        except Exception as e:
            logger.warning(f"Error enriching battle {bname}: {e}")
            saver.record_error(bid, str(e), final=False)

    return results


def _parse_participants(infobox: dict) -> list[dict]:
    """Parse combatant fields into participant records."""
    participants = []
    for side_label in ["side_a", "side_b"]:
        val = infobox.get(side_label, "")
        if not val:
            continue
        side = "A" if "a" in side_label else "B"
        # Split on <br/>, comma, bullet, etc.
        for part in re.split(r"<br\s*/?>|,|•|;", val):
            part = part.strip()
            if part and len(part) > 2:
                participants.append({"name": part, "side": side})
    return participants


def merge_enrichment_into_tables(
    war_enrichment_results: list[dict],
    battle_enrichment_results: list[dict],
    wars_df: pd.DataFrame,
    wp_df: pd.DataFrame,
    battles_df: pd.DataFrame,
    termination_df: pd.DataFrame,
    output_dir: Path,
) -> dict:
    """Merge Wikipedia enrichment back into processed tables.

    Args:
        war_enrichment_results: List of war-level enrichment dicts (with war_id).
        battle_enrichment_results: List of battle-level enrichment dicts (with battle_id).
        wars_df, wp_df, battles_df, termination_df: Source tables.
        output_dir: Where to write updated parquet files.

    Returns:
        Dict with summary of changes.
    """
    # Ensure battles has the new enrichment columns
    if battles_df is None:
        battles_df = pd.DataFrame()
    for col in [
        "wikipedia_title", "wikipedia_outcome", "wikipedia_location",
        "wikipedia_casualties_a", "wikipedia_casualties_b",
        "decisive_claimed_by_sources", "loser", "wikipedia_confidence",
    ]:
        if col not in battles_df.columns:
            battles_df[col] = ""
    for col in ["wikipedia_title", "wikipedia_outcome", "wikipedia_location",
                "wikipedia_casualties_a", "wikipedia_casualties_b",
                "decisive_claimed_by_sources", "loser", "wikipedia_confidence"]:
        if col in battles_df.columns:
            battles_df[col] = battles_df[col].astype(str)

    # Build lookups
    war_enrich = {}
    for r in war_enrichment_results:
        if r.get("war_id"):
            war_enrich[r["war_id"]] = r

    battle_enrich = {}
    for r in battle_enrichment_results:
        if r.get("battle_id"):
            battle_enrich[r["battle_id"]] = r

    # 1. Update wars.parquet
    updated_wars = wars_df.copy()
    for wid, data in war_enrich.items():
        infobox = data.get("infobox", {})
        classified = data.get("outcome_classified", {}) or {}
        idx = updated_wars[updated_wars["war_id"] == wid].index
        if len(idx) == 0:
            continue
        row_idx = int(idx[0])
        outcome_class = classified.get("outcome_class", "")
        if outcome_class:
            updated_wars.at[row_idx, "outcome_type"] = str(outcome_class)
        notes_parts = []
        if classified.get("is_decisive"):
            notes_parts.append("Wikipedia: decisive outcome")
        if classified.get("has_treaty"):
            notes_parts.append("Wikipedia: treaty signed")
        if classified.get("has_armistice"):
            notes_parts.append("Wikipedia: armistice")
        if classified.get("has_surrender"):
            notes_parts.append("Wikipedia: surrender")
        if notes_parts:
            existing = str(updated_wars.at[row_idx, "notes"]) if "notes" in updated_wars.columns else ""
            updated_wars.at[row_idx, "notes"] = (existing + "; " + "; ".join(notes_parts)).strip("; ")
        loc = data.get("location_clean") or infobox.get("place", "")
        current_region = (
            updated_wars.loc[row_idx, "region"] if "region" in updated_wars.columns else "unknown"
        )
        if loc and str(current_region) in ("unknown", "nan", ""):
            ll = loc.lower()
            if any(k in ll for k in ["europe", "france", "germany", "italy", "spain", "russia", "poland", "austria", "balkan", "scandinavia"]):
                updated_wars.at[row_idx, "region"] = "europe"
            elif any(k in ll for k in ["asia", "china", "japan", "india", "korea", "middle east", "persia", "arab", "israel", "turkey"]):
                updated_wars.at[row_idx, "region"] = "asia_mideast"
            elif any(k in ll for k in ["america", "mexico", "canada", "brazil", "argentina", "chile", "peru", "colombia"]):
                updated_wars.at[row_idx, "region"] = "americas"
            elif any(k in ll for k in ["africa", "ethiopia", "egypt", "libya", "algeria", "morocco", "angola"]):
                updated_wars.at[row_idx, "region"] = "africa"

    # 2. Update termination_events.parquet
    updated_term = termination_df.copy()
    for wid, data in war_enrich.items():
        idx = updated_term[updated_term["war_id"] == wid].index
        if len(idx) == 0:
            continue
        row_idx = int(idx[0])
        oc = data.get("outcome_classified", {}) or {}
        if oc.get("has_treaty"):
            updated_term.at[row_idx, "treaty_signed"] = "1"
        if oc.get("has_armistice"):
            updated_term.at[row_idx, "armistice_signed"] = "1"
        if oc.get("has_surrender"):
            updated_term.at[row_idx, "surrender_signed"] = "1"
        if oc.get("is_decisive"):
            notes_existing = str(updated_term.at[row_idx, "notes"]) if "notes" in updated_term.columns else ""
            updated_term.at[row_idx, "notes"] = (notes_existing + " Wikipedia: decisive outcome").strip()

    # 3. Update battles.parquet with battle enrichment
    battles_updated = 0
    if len(battles_df) > 0 and len(battle_enrich) > 0:
        for bid, data in battle_enrich.items():
            idx = battles_df[battles_df["battle_id"] == bid].index
            if len(idx) == 0:
                continue
            row_idx = int(idx[0])
            infobox = data.get("infobox", {}) or {}
            # Map IWB "victor" side-A/B to winner name
            wikipedia_title = data.get("title", "")
            if wikipedia_title and not battles_df.at[row_idx, "wikipedia_title"]:
                battles_df.at[row_idx, "wikipedia_title"] = str(wikipedia_title)
            outcome_raw = infobox.get("result", "")
            if outcome_raw and not battles_df.at[row_idx, "wikipedia_outcome"]:
                battles_df.at[row_idx, "wikipedia_outcome"] = str(outcome_raw)[:500]
            loc = infobox.get("place", "") or infobox.get("location", "")
            if loc and not battles_df.at[row_idx, "location"]:
                clean_loc = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]", r"\1", str(loc))
                clean_loc = re.sub(r"<[^>]+>", "", clean_loc)
                clean_loc = re.sub(r"'{2,}", "", clean_loc)
                clean_loc = re.sub(r"\s+", " ", clean_loc).strip()
                if clean_loc:
                    battles_df.at[row_idx, "location"] = clean_loc[:200]
                    battles_df.at[row_idx, "wikipedia_location"] = clean_loc[:200]
            if infobox.get("casualties1") and not battles_df.at[row_idx, "wikipedia_casualties_a"]:
                battles_df.at[row_idx, "wikipedia_casualties_a"] = str(infobox.get("casualties1"))[:200]
            if infobox.get("casualties2") and not battles_df.at[row_idx, "wikipedia_casualties_b"]:
                battles_df.at[row_idx, "wikipedia_casualties_b"] = str(infobox.get("casualties2"))[:200]
            oc = data.get("outcome_classified", {}) or {}
            if oc.get("is_decisive") and not battles_df.at[row_idx, "decisive_claimed_by_sources"]:
                battles_df.at[row_idx, "decisive_claimed_by_sources"] = "1"
            if "B" in (oc.get("winner_from_outcome", "") or "") and not battles_df.at[row_idx, "loser"]:
                battles_df.at[row_idx, "loser"] = str(oc.get("loser_from_outcome", ""))[:200]
            if not battles_df.at[row_idx, "wikipedia_confidence"]:
                battles_df.at[row_idx, "wikipedia_confidence"] = "C"
            battles_updated += 1

    # 4. Save updated tables
    output_dir.mkdir(parents=True, exist_ok=True)
    updated_wars.to_parquet(output_dir / "wars.parquet", index=False)
    if wp_df is not None and len(wp_df) > 0:
        wp_df.to_parquet(output_dir / "war_participants.parquet", index=False)
    if len(battles_df) > 0:
        battles_df.to_parquet(output_dir / "battles.parquet", index=False)
    if updated_term is not None and len(updated_term) > 0:
        updated_term.to_parquet(output_dir / "termination_events.parquet", index=False)

    # 5. Save raw enrichment results to interim parquet
    interim_dir = output_dir.parent / "interim"
    interim_dir.mkdir(parents=True, exist_ok=True)
    if war_enrichment_results:
        war_records = []
        for r in war_enrichment_results:
            war_records.append({
                "war_id": r.get("war_id", ""),
                "title": r.get("title", ""),
                "status": r.get("status", ""),
                "outcome_wikipedia": (r.get("outcome_wikipedia", "") or "")[:500],
                "location_clean": (r.get("location_clean", "") or "")[:500],
                "date_raw": (r.get("date_raw", "") or "")[:200],
                "outcome_class": (r.get("outcome_classified", {}) or {}).get("outcome_class", ""),
                "is_decisive": (r.get("outcome_classified", {}) or {}).get("is_decisive", False),
                "has_treaty": (r.get("outcome_classified", {}) or {}).get("has_treaty", False),
                "has_armistice": (r.get("outcome_classified", {}) or {}).get("has_armistice", False),
                "has_surrender": (r.get("outcome_classified", {}) or {}).get("has_surrender", False),
            })
        pd.DataFrame(war_records).to_parquet(interim_dir / "wikipedia_war_enrichment.parquet", index=False)
    if battle_enrichment_results:
        battle_records = []
        for r in battle_enrichment_results:
            infobox = r.get("infobox", {}) or {}
            oc = r.get("outcome_classified", {}) or {}
            battle_records.append({
                "battle_id": r.get("battle_id", ""),
                "war_id": r.get("war_id", ""),
                "title": r.get("title", ""),
                "status": r.get("status", ""),
                "outcome_raw": (infobox.get("result", "") or "")[:500],
                "place": (infobox.get("place", "") or "")[:500],
                "casualties_a": (infobox.get("casualties1", "") or "")[:200],
                "casualties_b": (infobox.get("casualties2", "") or "")[:200],
                "is_decisive": oc.get("is_decisive", False),
            })
        pd.DataFrame(battle_records).to_parquet(interim_dir / "wikipedia_battle_enrichment.parquet", index=False)

    wars_affected = len(war_enrich)
    regions_fixed = sum(
        1 for v in war_enrich.values()
        if v.get("location_clean") and str(v.get("location_clean", "")).strip()
    )
    return {
        "wars_updated": wars_affected,
        "battles_updated": battles_updated,
        "regions_corrected": regions_fixed,
    }


def run_enrichment(output_dir: Path, progress_dir: Path, max_wars: int = 0) -> dict:
    """Run the full Wikipedia enrichment pipeline.

    Args:
        output_dir: Where processed tables live.
        progress_dir: Where to save incremental progress.
        max_wars: Max interstate wars to enrich (0 = all).
    """
    progress_dir.mkdir(parents=True, exist_ok=True)

    wars = pd.read_parquet(output_dir / "wars.parquet") if (output_dir / "wars.parquet").exists() else pd.DataFrame()
    if len(wars) == 0:
        return {"error": "No wars data found"}

    battles = pd.read_parquet(output_dir / "battles.parquet") if (output_dir / "battles.parquet").exists() else pd.DataFrame()
    wp = pd.read_parquet(output_dir / "war_participants.parquet") if (output_dir / "war_participants.parquet").exists() else pd.DataFrame()
    term = pd.read_parquet(output_dir / "termination_events.parquet") if (output_dir / "termination_events.parquet").exists() else pd.DataFrame()

    # Build title mapping from IWB
    iwb_titles = pd.read_parquet(output_dir / "iwb_wikipedia_titles.parquet") if (output_dir / "iwb_wikipedia_titles.parquet").exists() else None

    title_map = {}
    if iwb_titles is not None:
        for _, r in iwb_titles.iterrows():
            wid = f"cow_iw_{int(r['cowNum'])}"
            title_map[wid] = r["candidate_title"]
        title_map["cow_iw_163"] = "Vietnam War"  # Override phase 2

    # Add known overrides for common mismatches
    OVERRIDES = {
        "cow_iw_1": "Franco-Spanish War (1823)",
        "cow_iw_4": "Russo-Turkish War (1828–1829)",
        "cow_iw_7": "Mexican–American War",
        "cow_iw_10": "Austro-Sardinian War",
        "cow_iw_16": "Roman Republic (1849–1850)",
        "cow_iw_19": "War of the Confederation",
        "cow_iw_28": "Second Italian War of Independence",
        "cow_iw_34": "Roman Question",
        "cow_iw_37": "Neapolitan War",
        "cow_iw_40": "Second French intervention in Mexico",
        "cow_iw_43": "Ecuadorian–Colombian War",
        "cow_iw_49": "Paraguayan War",
        "cow_iw_55": "Austro-Prussian War",
        "cow_iw_58": "Franco-Prussian War",
        "cow_iw_64": "War of the Pacific",
        "cow_iw_65": "Anglo-Egyptian War",
        "cow_iw_76": "Greco-Turkish War (1897)",
        "cow_iw_82": "Boxer Rebellion",
        "cow_iw_83": "Russian invasion of Manchuria",
        "cow_iw_85": "Russo-Japanese War",
        "cow_iw_97": "Italo-Turkish War",
        "cow_iw_100": "First Balkan War",
        "cow_iw_103": "Second Balkan War",
        "cow_iw_106": "World War I",
        "cow_iw_115": "Greco-Turkish War (1919–1922)",
        "cow_iw_121": "Second Sino-Japanese War",
        "cow_iw_124": "Chaco War",
        "cow_iw_127": "Second Italo-Ethiopian War",
        "cow_iw_133": "Battle of Lake Khasan",
        "cow_iw_136": "Battles of Khalkhin Gol",
        "cow_iw_139": "World War II",
        "cow_iw_142": "Winter War",
        "cow_iw_147": "Indo-Pakistani War of 1947–1948",
        "cow_iw_148": "1948 Arab–Israeli War",
        "cow_iw_151": "Korean War",
        "cow_iw_155": "Suez Crisis",
        "cow_iw_156": "Hungarian Revolution of 1956",
        "cow_iw_163": "Vietnam War",
        "cow_iw_169": "Six-Day War",
        "cow_iw_172": "War of Attrition",
        "cow_iw_175": "Football War",
        "cow_iw_178": "Bangladesh Liberation War",
        "cow_iw_181": "Yom Kippur War",
        "cow_iw_199": "Iran–Iraq War",
        "cow_iw_202": "Falklands War",
        "cow_iw_211": "Gulf War",
        "cow_iw_217": "Cenepa War",
        "cow_iw_223": "Kargil War",
        "cow_iw_225": "United States invasion of Afghanistan",
        "cow_iw_227": "Iraq War",
    }
    title_map.update(OVERRIDES)

    client = WikipediaClient(cache_dir=progress_dir / "cache")

    # Step 1: Enrich wars
    war_progress = progress_dir / "war_enrichment_progress.json"
    war_results = enrich_all_interstate_wars(
        client, wars, title_map, war_progress
    )

    # Step 2: Enrich battles (subset - those belonging to enriched wars)
    enriched_wids = {r["war_id"] for r in war_results}
    battle_progress = progress_dir / "battle_enrichment_progress.json"
    battle_results = []
    if len(battles) > 0:
        for wid in sorted(enriched_wids):
            batch = enrich_battles_for_war(client, wid, battles, battle_progress)
            battle_results.extend(batch)

    # Step 3: Merge back
    merge_result = merge_enrichment_into_tables(
        war_results, battle_results, wars, wp, battles, term, output_dir
    )

    return {
        "wars_enriched": len(war_results),
        "battles_enriched": len(battle_results),
        **merge_result,
    }
