// Neutral bridge v3. A missing/invalid extension leaves the original game UI intact.
(function () {
    var root = $.GetContextPanel();
    var lastHero = null;
    var generation = 0;
    // Internal identifiers from retail hero-name token keys, excluding search/sort keys.
    var officialHeroClasses = ["hero_akimbo", "hero_apocalypse", "hero_architect", "hero_artist", "hero_assassin", "hero_astro", "hero_atlas", "hero_baba", "hero_ballista", "hero_bebop", "hero_boho", "hero_bomber", "hero_bookworm", "hero_cadence", "hero_chessmaster", "hero_chrono", "hero_clawdril", "hero_coldmetal", "hero_cowboy", "hero_deadpack", "hero_demoman", "hero_doorman", "hero_drifter", "hero_druid", "hero_duo", "hero_dynamo", "hero_familiar", "hero_fencer", "hero_forge", "hero_fortuna", "hero_frank", "hero_gadgeteer", "hero_gadgetman", "hero_genericperson", "hero_ghost", "hero_gigawatt", "hero_glider", "hero_graf", "hero_gunner", "hero_gunslinger", "hero_haze", "hero_hijack", "hero_hornet", "hero_inferno", "hero_kali", "hero_kelvin", "hero_krill", "hero_lash", "hero_magician", "hero_mechaguy", "hero_mirage", "hero_nano", "hero_necro", "hero_nurse", "hero_opera", "hero_operative", "hero_orion", "hero_phalanx", "hero_phoenix", "hero_priest", "hero_punkgoat", "hero_ratking", "hero_revenant", "hero_rutger", "hero_sapper", "hero_shieldguy", "hero_shiv", "hero_skymonk", "hero_skyrunner", "hero_slingshot", "hero_slork", "hero_spade", "hero_swan", "hero_synth", "hero_targetdummy", "hero_tempest", "hero_tengu", "hero_test", "hero_thumper", "hero_tokamak", "hero_trapper", "hero_unicorn", "hero_vampire", "hero_vampirebat", "hero_vandal", "hero_viper", "hero_viscous", "hero_warden", "hero_werewolf", "hero_wraith", "hero_wrecker", "hero_yakuza", "hero_yamato", "hero_zealot"];
    function heroClass(panel) {
        for (var depth = 0; panel && depth < 16; depth++, panel = panel.GetParent()) {
            var found = officialHeroClasses.filter(function (name) { return panel.BHasClass(name); });
            if (found.length === 1) return found[0];
            if (found.length > 1) return null;
        }
        return null;
    }
    function update() {
        if (!root || !root.IsValid()) return;
        try {
            var hero = heroClass(root);
            var host = root.FindChildInLayoutFile("IndependentWordmarkHost");
            if (host && hero !== lastHero) {
                lastHero = hero;
                root.RemoveClass("IndependentWordmarkActive");
                host.RemoveAndDeleteChildren();
                if (hero) {
                    // A fresh panel avoids stale layout caching when revisiting a hero.
                    generation++;
                    var inner = $.CreatePanel("Panel", host, "IndependentWordmarkContent_" + generation);
                    var ok = inner.BLoadLayout("file://{resources}/layout/hero_wordmark_extensions/" + hero + ".xml", false, false);
                    if (ok && inner.FindChildInLayoutFile("IndependentWordmarkReady"))
                        root.AddClass("IndependentWordmarkActive");
                }
            }
        } catch (error) {
            root.RemoveClass("IndependentWordmarkActive");
        }
        $.Schedule(0.25, update);
    }
    update();
})();
