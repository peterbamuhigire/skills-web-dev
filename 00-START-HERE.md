<VirtualHost *:80>
    ServerName demo.pibid.org
    DocumentRoot /var/www/html/birdcerp/public
    <Directory /var/www/html/birdcerp/public>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
        <IfModule mod_rewrite.c>
            RewriteEngine On
            RewriteCond %{REQUEST_FILENAME} !-f
            RewriteCond %{REQUEST_FILENAME} !-d
            RewriteRule ^ index.php [L]
        </IfModule>
    </Directory>
    <FilesMatch "^\.env">
        Require all denied
    </FilesMatch>
    <DirectoryMatch "^/.*/\.git/">
        Require all denied
    </DirectoryMatch>
    ErrorLog ${APACHE_LOG_DIR}/demo.birdc.ug-error.log
    CustomLog ${APACHE_LOG_DIR}/demo.birdc.ug-access.log combined
    <IfModule mod_headers.c>
        Header always set X-Content-Type-Options "nosniff"
        Header always set X-Frame-Options "SAMEORIGIN"
        Header always set X-XSS-Protection "1; mode=block"
        Header always set Referrer-Policy "strict-origin-when-cross-origin"
    </IfModule>
RewriteCond %{SERVER_NAME} =demo.birdc.ug
RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>