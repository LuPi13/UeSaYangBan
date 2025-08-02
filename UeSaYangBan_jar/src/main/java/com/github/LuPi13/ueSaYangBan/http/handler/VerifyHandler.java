package com.github.LuPi13.ueSaYangBan.http.handler;

import fi.iki.elonen.NanoHTTPD;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.plugin.Plugin;
import org.json.JSONObject;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.logging.Level;

public class VerifyHandler implements IHttpRequestHandler {

    private final Plugin plugin;

    public VerifyHandler(Plugin plugin) {
        this.plugin = plugin;
    }

    @Override
    public NanoHTTPD.Response handle(NanoHTTPD.IHTTPSession session) {
        HashMap<String, String> files = new HashMap<>();
        try {
            session.parseBody(files);

            // The path to this file is stored in the 'files' map with the key "postData".
            String body = files.get("postData");
            if ((body == null) || body.isEmpty()) {
                throw new IOException("POST body was empty or not found");
            }

            JSONObject json = new JSONObject(body);

            String token = json.getString("token");
            String name = json.getString("name");

            if (verifyToken(token)) {
                if (saveLink(json)) {
                    removeTempToken();
                }
                else {
                    plugin.getLogger().log(Level.SEVERE, "Failed to save link for name: " + name);
                    return NanoHTTPD.newFixedLengthResponse(NanoHTTPD.Response.Status.INTERNAL_ERROR, "application/json", "{\"error\":\"failed_to_save_link\"}");
                }
                return NanoHTTPD.newFixedLengthResponse(NanoHTTPD.Response.Status.OK, "application/json", "{\"status\":\"success\"}");
            } else {
                return NanoHTTPD.newFixedLengthResponse(NanoHTTPD.Response.Status.UNAUTHORIZED, "application/json", "{\"error\":\"invalid_token\"}");
            }
        } catch (Exception e) {
            plugin.getLogger().log(Level.SEVERE, "Error processing /verify request", e);
            return NanoHTTPD.newFixedLengthResponse(NanoHTTPD.Response.Status.INTERNAL_ERROR, "application/json", "{\"error\":\"internal_server_error\"}");
        }
    }

    private boolean verifyToken(String token) {
        File tempLinksFile = new File(plugin.getDataFolder(), "temp_links.yml");
        if (!tempLinksFile.exists()) {
            return false;
        }
        try {
            YamlConfiguration tempConfig = YamlConfiguration.loadConfiguration(tempLinksFile);
            long timeStamp = tempConfig.getLong("time_stamp");
            long expirationTime = plugin.getConfig().getLong("verify-token-expire-time", 300000);
            if (System.currentTimeMillis() - timeStamp > expirationTime) {
                return false; // Token has expired
            }
            String tempToken = tempConfig.getString("token");
            return token.equals(tempToken);
        } catch (Exception e) {
            plugin.getLogger().log(Level.SEVERE, "Error verifying token", e);
            return false;
        }
    }

    private boolean saveLink(JSONObject json) {
        String name = json.getString("name");
        String botHttpHost = json.getString("bot_http_host");
        int botHttpPort = json.getInt("bot_http_port");
        long discordServerId = json.getLong("discord_server_id");
        long discordChannelId = json.getLong("discord_channel_id");
        String type = json.optString("discord_channel_type", "default");
        String purpose = json.optString("purpose", "default");

        File linksFile = new File(plugin.getDataFolder(), "links.yml");
        YamlConfiguration linksConfig = YamlConfiguration.loadConfiguration(linksFile);
        if (linksConfig.contains(name)) {
            plugin.getLogger().log(Level.SEVERE, "Link already exists in config");
            throw new IllegalArgumentException("Link with name '" + name + "' already exists.");
        }
        linksConfig.set(name + ".bot_http_host", botHttpHost);
        linksConfig.set(name + ".bot_http_port", botHttpPort);
        linksConfig.set(name + ".discord_server_id", discordServerId);
        linksConfig.set(name + ".discord_channel_id", discordChannelId);
        linksConfig.set(name + ".type", type);
        linksConfig.set(name + ".purpose", purpose);

        try {
            linksConfig.save(linksFile);
            return true;
        } catch (IOException e) {
            plugin.getLogger().log(Level.SEVERE, "Failed to save link", e);
            return false;
        }
    }

    private void removeTempToken() {
        File tempLinksFile = new File(plugin.getDataFolder(), "temp_links.yml");
        if (tempLinksFile.exists()) {
            tempLinksFile.delete();
        }
    }
}