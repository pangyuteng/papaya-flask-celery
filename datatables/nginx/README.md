https://www.digitalocean.com/community/tutorials/how-to-set-up-password-authentication-with-nginx-on-ubuntu-14-04

```
echo -n 'hohoho:' >> .htpasswd
openssl passwd -apr1 >> .htpasswd
```

