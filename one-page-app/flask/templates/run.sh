echo workdir {{workdir}}
echo task_id {{task_id}}
echo full_name {{full_name}}
echo extra_sauce {{extra_sauce}}

export extra_sauce={{extra_sauce}}

sleep 10

if [ ${extra_sauce} == 'YES' ]; then
    echo extra sauce is sinful >&2
    exit 1
fi