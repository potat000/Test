@ECHO OFF

set result=false
if "%CONDA_DEFAULT_ENV%" == "" set result=true
if "%CONDA_DEFAULT_ENV%" == "base" set result=true
if "%result%" == "true" GOTO NOENV
:YESENV
    @ECHO Not create conda env.
    set result=false
    if "%CONDA_DEFAULT_ENV%" == "Env" set result=true
    if "%CONDA_DEFAULT_ENV%" == "%cd%\Env" set result=true
    if not "%result%" == "true" (
        @ECHO Not create conda env.
        ECHO activate %CONDA_DEFAULT_ENV% > Activate%CONDA_DEFAULT_ENV%.bat
    )
    GOTO END
:NOENV
    @ECHO Create conda env.
    if exist "%cd%\Env" GOTO NOCREATE
    :CREATEENV
        echo if you are run in anaconda3, you should execute ActivateEnv.bat and run Configure.bat again.
        conda create -p Env python=3.7.3 -y
        GOTO END2
    :NOCREATE
        GOTO END2
    :END2
    call Env\Scripts\activate.bat Env
    if not "%errorlevel%" == "0" (
        echo if you are run in anaconda3, it may cause 'Env\Scripts\activate.bat' error, bat it's ok, Env is activating.
        echo if you are run in anaconda3, you should execute Configure.bat again.
        conda activate "%cd%\Env"
        GOTO END3
    )
    GOTO END
:END

@ECHO ON

:: python -m pip install --upgrade pip

pip install -r REQUIREMENTS.txt

python manage.py migrate

python manage.py search_apps

