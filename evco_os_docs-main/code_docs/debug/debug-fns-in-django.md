# debugging functions in django

in any module, e.g. cportal.views or customer.views

1. **create a function**
    views.py:
    ```python

    def testFunction(request):
    try:
        x = 5
        x *= 2 # press F9 on this line to create breakpoint that triggers in debug
        return f'hey this will print in your browser: x = {x}'
    except Exception as e:
        return f'something went wrong: {e}'
    ```

2. **add to urls**
    urls.py:
    ```python
    import views
    
    test_patterns = [
        # test
        re_path(r"TEST", views.testFunction)
    ]
    ```

3. **configure debug in vscode**
    /.vscode/launch.json:
    ```json
    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Django server",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/manage.py", 
                // might have to edit "program" based on the folder you open in vscode
                "args": [
                    "runserver",
                    "--insecure"
                ],
                "django": true,
                "justMyCode": true
            },
        ]
    }
    ```

4. **debug**
    press F5 on keyboard
    