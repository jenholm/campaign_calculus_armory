/**
 * Historical event annotations for each preset.
 * Moved out of war_simulation.js to separate engine from UI data.
 *
 * Source: Historical research aligned with paper Table 4.
 */
window.HISTORICAL_EVENTS = {
    "gulf_war_1991": [
        { month: 0, label: "Invasion of Kuwait", type: "trigger" },
        { month: 5, label: "UN Resolution 678", type: "political" },
        { month: 7, label: "Operation Desert Shield", type: "military" },
        { month: 13, label: "Air campaign begins", type: "shock" },
        { month: 14, label: "Ground war begins (100 hours)", type: "shock" },
        { month: 14.5, label: "Kuwait liberated", type: "outcome" },
        { month: 15, label: "Ceasefire declared", type: "outcome" }
    ],
    "vietnam_war": [
        { month: 0, label: "Gulf of Tonkin Resolution", type: "trigger" },
        { month: 12, label: "US troop buildup begins", type: "military" },
        { month: 24, label: "Tet Offensive", type: "shock" },
        { month: 36, label: "Vietnamization begins", type: "political" },
        { month: 48, label: "Paris Peace Accords", type: "political" },
        { month: 60, label: "US withdrawal complete", type: "outcome" },
        { month: 108, label: "Fall of Saigon", type: "outcome" }
    ],
    "wwi": [
        { month: 0, label: "Assassination of Franz Ferdinand", type: "trigger" },
        { month: 1, label: "Mobilization cascade", type: "military" },
        { month: 4, label: "Race to the Sea", type: "military" },
        { month: 18, label: "Verdun offensive", type: "shock" },
        { month: 22, label: "Somme offensive", type: "shock" },
        { month: 36, label: "French mutinies", type: "political" },
        { month: 42, label: "US enters war", type: "political" },
        { month: 54, label: "German spring offensive fails", type: "shock" },
        { month: 57, label: "Hundred Days Offensive", type: "shock" },
        { month: 58, label: "Armistice", type: "outcome" }
    ],
    "franco_prussian": [
        { month: 0, label: "Ems Dispatch", type: "trigger" },
        { month: 1, label: "Prussian mobilization", type: "military" },
        { month: 2, label: "Battle of Wissembourg", type: "shock" },
        { month: 3, label: "Battle of Sedan", type: "shock" },
        { month: 3.5, label: "Napoleon III captured", type: "outcome" },
        { month: 4, label: "Government of National Defense", type: "political" },
        { month: 5, label: "Siege of Paris begins", type: "military" },
        { month: 9, label: "Paris falls", type: "outcome" }
    ],
    "korean_war": [
        { month: 0, label: "North Korean invasion", type: "trigger" },
        { month: 3, label: "Pusan Perimeter", type: "military" },
        { month: 4, label: "Inchon landing", type: "shock" },
        { month: 5, label: "Seoul recaptured", type: "shock" },
        { month: 6, label: "UN crosses 38th parallel", type: "military" },
        { month: 8, label: "Chinese intervention", type: "political" },
        { month: 12, label: "Stalemate begins", type: "military" },
        { month: 36, label: "Armistice signed", type: "outcome" }
    ],
    "iran_iraq": [
        { month: 0, label: "Iraqi invasion of Iran", type: "trigger" },
        { month: 6, label: "Iranian counteroffensive", type: "military" },
        { month: 18, label: "Stalemate along border", type: "military" },
        { month: 36, label: "Tanker War begins", type: "military" },
        { month: 60, label: "Iranian offensives", type: "shock" },
        { month: 84, label: "UN Resolution 598", type: "political" },
        { month: 96, label: "Ceasefire", type: "outcome" }
    ],
    "wwii": [
        { month: 0, label: "Germany invades Poland", type: "trigger" },
        { month: 9, label: "Fall of France", type: "shock" },
        { month: 12, label: "Battle of Britain", type: "shock" },
        { month: 21, label: "Operation Barbarossa", type: "military" },
        { month: 33, label: "Battle of Midway", type: "shock" },
        { month: 45, label: "Stalingrad surrender", type: "outcome" },
        { month: 57, label: "D-Day Normandy", type: "shock" },
        { month: 68, label: "Germany surrenders", type: "outcome" },
        { month: 72, label: "Japan surrenders", type: "outcome" }
    ]
};
