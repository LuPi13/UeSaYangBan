package com.github.LuPi13.ueSaYangBan.http.handler;

import fi.iki.elonen.NanoHTTPD;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.plugin.Plugin;
import org.json.JSONObject;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.logging.Level;

public class UnlinkHandler implements IHttpRequestHandler {

    private final Plugin plugin;

    public UnlinkHandler(Plugin plugin) {
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

            String name = json.getString("name");

            File linksFile = new File(plugin.getDataFolder(), "links.yml");
            YamlConfiguration linksConfig = YamlConfiguration.loadConfiguration(linksFile);



            if (name != null && linksConfig.contains(name)) {
                // Remove the link for the given name
                linksConfig.set(name, null);
                try {
                    linksConfig.save(linksFile);
                } catch (IOException e) {
                    plugin.getLogger().log(Level.SEVERE, "Failed to save links.yml after unlinking", e);
                    return NanoHTTPD.newFixedLengthResponse(NanoHTTPD.Response.Status.INTERNAL_ERROR, "application/json", "{\"error\":\"failed_to_remove_links\"}");
                }
                return NanoHTTPD.newFixedLengthResponse(NanoHTTPD.Response.Status.OK, "application/json", "{\"status\":\"unlinked\"}");

            } else {
                return NanoHTTPD.newFixedLengthResponse(NanoHTTPD.Response.Status.NOT_FOUND, "application/json", "{\"error\":\"name_not_found\"}");
            }
        } catch (Exception e) {
            plugin.getLogger().log(Level.SEVERE, "Error processing /verify request", e);
            return NanoHTTPD.newFixedLengthResponse(NanoHTTPD.Response.Status.INTERNAL_ERROR, "application/json", "{\"error\":\"internal_server_error\"}");
        }
    }
}