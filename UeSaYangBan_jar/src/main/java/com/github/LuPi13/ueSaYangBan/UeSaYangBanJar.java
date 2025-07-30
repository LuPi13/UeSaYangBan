package com.github.LuPi13.ueSaYangBan;

import com.github.LuPi13.ueSaYangBan.commands.LinkDiscord;
import com.github.LuPi13.ueSaYangBan.http.VerificationServer;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.File;
import java.io.IOException;
import java.util.logging.Level;

public final class UeSaYangBanJar extends JavaPlugin {

    private VerificationServer verificationServer;

    @Override
    public void onEnable() {
        // Plugin startup logic
        if (!getDataFolder().exists()) {
            getDataFolder().mkdirs();
        }

        // Load the configuration file
        saveDefaultConfig();
        getConfig().options().copyDefaults(true);
        saveConfig();

        File dataFolder = getDataFolder();

        // Start the HTTP server
        try {
            int port = getConfig().getInt("http-port", 8123); // Default port is 8123, can be configured in config.yml
            verificationServer = new VerificationServer(port, this);
            verificationServer.start();
        } catch (IOException e) {
            getLogger().log(Level.SEVERE, e.toString());
        }

        // Register command
        this.getCommand("linkdiscord").setExecutor(new LinkDiscord(this));
    }

    @Override
    public void onDisable() {
        // Plugin shutdown logic
        if (verificationServer != null) {
            verificationServer.stop();
        }
    }
}

