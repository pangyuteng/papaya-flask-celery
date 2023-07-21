```
https://github.com/rii-mango/Papaya/wiki/Configuration#images
https://github.com/rii-mango/Papaya/wiki/How-To-Make-a-Color-Table

```

```
params["luts"] = [{"name": "Custom", "data": {{ contour_lut }} }];
params["{{ contour_basename }}"]  = {"lut":"Custom","alpha":0.5,"min":{{min_val}}, "max":{{max_val}} };

```

```
lut = []
for x in roi_list:
    r,g,b = x['color']
    val = n+1
    normval = n/(len(roi_list)-1)
    lut.append([normval,r,g,b])

min_val=0.99
max_val=len(roi_list)+0.01
contour_lut = str(lut)

```


