package com.github.LuPi13.ueSaYangBan.commands;

import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.event.ClickEvent;
import net.kyori.adventure.text.event.HoverEvent;
import net.kyori.adventure.text.format.NamedTextColor;
import org.bukkit.Bukkit;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.plugin.java.JavaPlugin;
import org.jetbrains.annotations.NotNull;

import java.io.File;
import java.io.IOException;
import java.util.Base64;
import java.util.UUID;
import java.util.logging.Level;

public class LinkDiscord implements CommandExecutor {

    private final JavaPlugin plugin;

    public LinkDiscord(JavaPlugin plugin) {
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(@NotNull CommandSender sender, @NotNull Command command, @NotNull String label, @NotNull String[] args) {
        if (!sender.hasPermission("uesayangban.linkdiscord")) {
            sender.sendMessage(Component.text("해당 명령어를 실행하기 위한 권한이 없습니다! (uesayangban.linkdiscord)", NamedTextColor.RED));
            return true;
        }


        // 토큰 생성; 랜덤 UUID
        String token = UUID.randomUUID().toString();

        // 서버 주소 생성
        String serverIp = Bukkit.getServer().getIp(); // server.properties에서 ip를 가져오므로 반드시 명시되어 있어야 함.
        int httpPort = plugin.getConfig().getInt("http-port");

        // JSON 문자열 생성
        String jsonString = String.format("""
                {
                    "mc_server_address": "%s",
                    "mc_http_port": %d,
                    "token": "%s"
                }""", serverIp, httpPort, token);

        // Base64 encode
        String base64EncodedString = Base64.getEncoder().encodeToString(jsonString.getBytes());
        // clickable 컴포넌트 생성
        Component clickableMessage = Component.text(base64EncodedString, NamedTextColor.GREEN)
                .hoverEvent(HoverEvent.showText(Component.text("클릭하여 복사", NamedTextColor.WHITE)))
                .clickEvent(ClickEvent.copyToClipboard(base64EncodedString));

        // 임시 파일 저장
        boolean saved = saveToken(token);
        if (!saved) {
            sender.sendMessage(Component.text("토큰을 저장하는 중 오류가 발생했습니다.", NamedTextColor.RED));
            return true;
        }

        // 메시지 전송
        sender.sendMessage("아래 문자열을 클릭해 복사하여 디스코드 봇에게 보내세요:");
        sender.sendMessage(clickableMessage);

        return true;
    }

    /**
     * 토큰 정보를 temp_links.yml 파일에 저장합니다.
     *
     * @param token 저장할 토큰
     * @return 저장 성공 여부
     */
    private boolean saveToken(String token) {
        try {
            File tempLinksFile = new File(plugin.getDataFolder(), "temp_links.yml");
            FileConfiguration config = YamlConfiguration.loadConfiguration(tempLinksFile);
            config.set("token", token);
            config.set("status", "PENDING");
            config.set("time_stamp", System.currentTimeMillis());
            config.save(tempLinksFile);
            return true;
        } catch (IOException e) {
            plugin.getLogger().log(Level.SEVERE, e.toString());
            return false;
        }
    }
}