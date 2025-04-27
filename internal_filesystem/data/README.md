Apps can write their data (like settings) here, in a subfolder of their reversed fully qualified name, such as:

/internal_filesystem/com.example.app1/settings.json may contain:

{
"server": "example.com",
"port" : 443
}
