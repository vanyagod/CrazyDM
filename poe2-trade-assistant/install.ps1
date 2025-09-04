# PoE2 Trade Assistant - PowerShell Setup Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " PoE2 Trade Assistant - Setup" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка Python
Write-Host "Проверка Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python не найден!" -ForegroundColor Red
    Write-Host "Скачайте и установите Python с python.org" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host ""

# Функция для установки пакета с проверкой
function Install-Package {
    param($PackageName, $DisplayName)
    
    Write-Host "Установка $DisplayName..." -ForegroundColor Yellow
    try {
        python -m pip install $PackageName 2>&1 | Out-Null
        Write-Host "✅ $DisplayName установлен" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Ошибка установки $DisplayName" -ForegroundColor Red
        return $false
    }
}

# Обновление pip
Write-Host "Обновление pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip | Out-Null

# Установка пакетов по порядку
$packages = @(
    @("requests", "Requests (HTTP клиент)"),
    @("aiohttp", "AioHTTP (асинхронный HTTP)"),
    @("pydantic>=2.5.0", "Pydantic (валидация данных)"),
    @("pydantic-settings", "Pydantic Settings"),
    @("python-dotenv", "Python DotEnv"),
    @("typer", "Typer (CLI)"),
    @("rich", "Rich (красивый вывод)")
)

$failed = @()
foreach ($package in $packages) {
    if (-not (Install-Package $package[0] $package[1])) {
        $failed += $package[1]
    }
}

Write-Host ""

# Проверка установки
Write-Host "Проверка установки..." -ForegroundColor Yellow
try {
    python -c "import requests, aiohttp, pydantic, typer, rich; print('✅ Все основные модули работают!')" 2>&1
    $testResult = $LASTEXITCODE
    
    if ($testResult -eq 0) {
        Write-Host "✅ Установка успешно завершена!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Теперь вы можете запустить:" -ForegroundColor Cyan
        Write-Host "  python run.py gui                    - Графический интерфейс" -ForegroundColor White
        Write-Host "  python run.py search `"item name`"     - Поиск через CLI" -ForegroundColor White  
        Write-Host "  python demo.py                       - Демонстрация" -ForegroundColor White
    } else {
        throw "Модули не импортируются"
    }
    
} catch {
    Write-Host "❌ Проблемы с импортом модулей" -ForegroundColor Red
    if ($failed.Count -gt 0) {
        Write-Host "Не удалось установить: $($failed -join ', ')" -ForegroundColor Red
    }
    Write-Host "Попробуйте установить вручную:" -ForegroundColor Yellow
    Write-Host "  python -m pip install requests aiohttp pydantic pydantic-settings typer rich" -ForegroundColor White
}

Write-Host ""
Read-Host "Нажмите Enter для завершения"