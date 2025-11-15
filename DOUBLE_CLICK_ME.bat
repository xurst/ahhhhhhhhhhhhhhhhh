@echo off
setlocal enabledelayedexpansion

:: Get script directory and project root
set "ScriptDir=%~dp0"
if "%ScriptDir:~-1%"=="\" set "ScriptDir=%ScriptDir:~0,-1%"
for %%I in ("%ScriptDir%") do set "ProjectRoot=%%~fI"

set "PsToolsFolder=%ProjectRoot%\src\modules\PSTools"
set "PsPasswdExe=%PsToolsFolder%\PsPasswd.exe"
set "PasswdLog=%PsToolsFolder%\PsPasswd.log"

:: Validate PsPasswd.exe
if not exist "%PsPasswdExe%" (
    echo ERROR: PsPasswd.exe not found at:
    echo "%PsPasswdExe%"
    echo Please place it in src\modules\PSTools\
    pause
    exit /b 1
)

:: ==========================================================
:: AUTO-DETECT LOCAL COMPUTER NAME
:: ==========================================================
for /f "tokens=2 delims==" %%a in ('wmic computersystem get name /value 2^>nul') do set "LocalComputer=%%a"
if not defined LocalComputer (
    echo WARNING: Could not detect computer name. Using %COMPUTERNAME%
    set "LocalComputer=%COMPUTERNAME%"
)

echo ===============================
echo   PsPasswd Utility Runner
echo ===============================
echo.
echo Detected local computer: %LocalComputer%
echo.

:: ==========================================================
:: FETCH LIST OF LOCAL USER ACCOUNTS
:: ==========================================================
echo Fetching local user accounts...
set "UserCount=0"
set "UserList="

:: Use 'net user' to get local accounts (skip domain lines if any)
for /f "skip=4 tokens=1-3" %%a in ('net user ^| findstr /v /c:"The command completed" /c:"---"') do (
    if not "%%a"=="" if "%%a" neq "User" (
        set /a UserCount+=1
        set "UserList[!UserCount!]=%%a"
        if not "%%b"=="" (
            set /a UserCount+=1
            set "UserList[!UserCount!]=%%b"
        )
        if not "%%c"=="" (
            set /a UserCount+=1
            set "UserList[!UserCount!]=%%c"
        )
    )
)

:: Remove empty/invalid entries and rebuild clean list
set "ValidCount=0"
for /l %%i in (1,1,%UserCount%) do (
    if defined UserList[%%i] (
        set "name=!UserList[%%i]!"
        if "!name:~0,1!" neq "*" if "!name!" neq "" (
            set /a ValidCount+=1
            set "CleanUser[!ValidCount!]=!name!"
        )
    )
)

if %ValidCount% EQU 0 (
    echo ERROR: No local user accounts found.
    pause
    exit /b 1
)

:: ==========================================================
:: DISPLAY USERS & LET USER CHOOSE
:: ==========================================================
echo.
echo Available local user accounts:
echo.
for /l %%i in (1,1,%ValidCount%) do (
    echo    %%i. !CleanUser[%%i]!
)
echo.

:prompt_user
set /p "Choice=Select a user (1-%ValidCount%): "
if not defined Choice goto :prompt_user

for /f "delims=0123456789" %%i in ("%Choice%") do (
    echo Invalid input. Please enter a number.
    goto :prompt_user
)

if %Choice% LSS 1 goto :prompt_user
if %Choice% GTR %ValidCount% goto :prompt_user

set "AccountUser=!CleanUser[%Choice%]!"

:: ==========================================================
:: TARGET COMPUTER: Default to local, allow override
:: ==========================================================
echo.
echo Target computer (default: %LocalComputer%):
set /p "TargetInput=Press Enter for local, or type remote name: "
if not defined TargetInput (
    set "TargetComputer="
) else (
    set "TargetComputer=%TargetInput%"
)

:: ==========================================================
:: NEW PASSWORD
:: ==========================================================
echo.
set "NewPassword="
set /p "NewPassword=Enter new password (leave blank for NULL): "

:: ==========================================================
:: CONFIRM
:: ==========================================================
echo.
echo Summary:
if defined TargetComputer (
    echo Target Computer: \\%TargetComputer%
) else (
    echo Target Computer: [LOCAL]
)
echo Username: %AccountUser%
if "%NewPassword%"=="" (
    echo New password: [NULL/EMPTY]
) else (
    echo New password: [HIDDEN]
)
echo.

choice /m "Proceed?"
if errorlevel 2 (
    echo Cancelled.
    pause
    exit /b 0
)

:: ==========================================================
:: RUN PsPasswd
:: ==========================================================
echo Running PsPasswd...
echo =============================== >> "%PasswdLog%"
echo [%DATE% %TIME%] Session Start >> "%PasswdLog%"
if defined TargetComputer (
    echo Target: \\%TargetComputer% >> "%PasswdLog%"
) else (
    echo Target: [LOCAL] >> "%PasswdLog%"
)
echo Username: %AccountUser% >> "%PasswdLog%"
echo ------------------------------- >> "%PasswdLog%"

if defined TargetComputer (
    "%PsPasswdExe%" \\%TargetComputer% %AccountUser% %NewPassword% >> "%PasswdLog%" 2>&1
) else (
    "%PsPasswdExe%" %AccountUser% %NewPassword% >> "%PasswdLog%" 2>&1
)

echo ------------------------------- >> "%PasswdLog%"
echo [End] >> "%PasswdLog%"
echo =============================== >> "%PasswdLog%"

echo.
echo Done! Log saved to: %PasswdLog%
echo.

pause
exit /b 0