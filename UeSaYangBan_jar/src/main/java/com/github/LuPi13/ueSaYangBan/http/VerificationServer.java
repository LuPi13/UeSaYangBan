package com.github.LuPi13.ueSaYangBan.http;

import com.github.LuPi13.ueSaYangBan.http.handler.IHttpRequestHandler;
import com.github.LuPi13.ueSaYangBan.http.handler.UnlinkHandler;
import com.github.LuPi13.ueSaYangBan.http.handler.VerifyHandler;
import fi.iki.elonen.NanoHTTPD;
import org.bukkit.plugin.Plugin;

import java.util.HashMap;
import java.util.Map;

public class VerificationServer extends NanoHTTPD {

    private final Map<String, IHttpRequestHandler> handlers = new HashMap<>();

    public VerificationServer(int port, Plugin plugin) {
        super(port);
        // Register all handlers
        registerHandler("/verify", new VerifyHandler(plugin));
        registerHandler("/unlink", new UnlinkHandler(plugin));
    }

    private void registerHandler(String uri, IHttpRequestHandler handler) {
        handlers.put(uri, handler);
    }

    @Override
    public Response serve(IHTTPSession session) {
        String uri = session.getUri();
        IHttpRequestHandler handler = handlers.get(uri);

        if (handler != null) {
            // Check for the correct method (e.g., POST for /verify)
            if (Method.POST.equals(session.getMethod()) && "/verify".equals(uri)) {
                return handler.handle(session);
            } else if (Method.POST.equals(session.getMethod()) && "/unlink".equals(uri)) {
                return handler.handle(session);
            }
            // If method does not match, return a 405 Method Not Allowed error
            return newFixedLengthResponse(Response.Status.METHOD_NOT_ALLOWED, MIME_PLAINTEXT, "Method Not Allowed");
        }

        // If no handler is found, return a 404 Not Found error
        return newFixedLengthResponse(Response.Status.NOT_FOUND, MIME_PLAINTEXT, "Not Found");
    }
}