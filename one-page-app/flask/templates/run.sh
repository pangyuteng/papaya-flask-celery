echo workdir {{workdir}}
echo task_id {{task_id}}
echo full_name {{full_name}}
echo extra_sauce {{extra_sauce}}

export extra_sauce={{extra_sauce}}

if [ ${extra_sauce} == 'YES' ]; then
    exit 1
fi