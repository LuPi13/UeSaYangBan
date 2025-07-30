package com.github.LuPi13.ueSaYangBan.http.handler;

import fi.iki.elonen.NanoHTTPD;

public interface IHttpRequestHandler {
    NanoHTTPD.Response handle(NanoHTTPD.IHTTPSession session);
}
