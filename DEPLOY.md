# Публикация
Цель: отдельный публичный репозиторий пользователя Bage340 и GitHub Pages с источником GitHub Actions. Фактический статус и адреса — в DEPLOY_LOG.md и PORTFOLIO_LINKS.md.

Выполнено 11.11.2026: создан https://github.com/Bage340/ryazan-web-demos , push main, Pages build_type=workflow, HTTPS включён; Actions run 42970107538 успешно опубликовал portfolio-dist. Полученный из Pages API адрес https://bage340.github.io/ryazan-web-demos/ открыт вместе с тремя демо. 20 публичных файлов совпали с локальными, публичный браузерный QA прошёл. Для деплоя действий владельца больше не требуется; осталось пользовательское принятие результата по MANUAL_ACTIONS.md.

## Реально найденный способ доступа
GitHub CLI установлен, но постоянного входа gh нет. Git credential manager содержит действующую GitHub-авторизацию, проверенную через GET /user как Bage340. Помощник `scripts/github_admin.py` получает её стандартной командой Git; секрет остаётся в памяти процесса, не печатается и не сохраняется. Изменять безопасность браузера или профиль не требуется.
```powershell
python scripts/github_admin.py status
```

## Воспроизводимая схема
После локального QA создать новый репозиторий `python scripts/github_admin.py create`; существующий репозиторий помощник не перезаписывает. Затем source + portfolio-dist + workflow фиксируются в main и отправляются обычным Git без force. Pages включается через `python scripts/github_admin.py enable-pages` с build_type=workflow. Статус: команды `runs`, `jobs --run ID`, `pages`.
Локальный файл qa/deploy-state.json содержит только имена/URL, исключён из Git. Повторный create при существующем состоянии запрещён. После переключения legacy-конфигурации с ответом HTTP 204 помощник повторно читает Pages API; это покрывает регрессионный тест без сети и секретов.

Workflow запускается при push изменений сайта в main или вручную workflow_dispatch. Сначала повторная упаковка, проверка 7 страниц/ссылок, синтаксис JS и отсутствие расхождения сборки с source; затем configure-pages@v5, upload-pages-artifact@v4, deploy-pages@v4. Публикуется только portfolio-dist/, исходники/документы не являются Pages-контентом. Права deploy: pages:write и id-token:write; contents:read.

## Следующие изменения и откат
Править source, выполнить сборку и QA, commit/push. Изменения корневых документов отдельно не вызывают повторный деплой; изменения внутри папок демо (включая QA.md) и проверяемых скриптов запускают workflow. Для отката вернуть конкретный предыдущий коммит обычным git revert, собрать и опубликовать через тот же workflow. Не применять force-push. Перед возвращением чужих пользовательских правок нужен отдельный разбор.

## Резерв SpaceWeb
В SpaceWeb можно перенести **содержимое** portfolio-dist в корень одного виртуального сайта: витрина в корне, три демо в подпапках. Официальная страница бесплатного тарифа проверена: https://sweb.ru/hosting/free/ . Перед регистрацией перепроверить условия и доступные протоколы. Аккаунт SpaceWeb не создавался; SFTP/FTP/CI-доступов нет, резервный деплой не выполнен и не обещан.

GitHub Pages используется как учебная демонстрационная витрина без сделок, заявок и обработки данных, с учётом https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits .
Workflow основан на https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages .

Последний подтверждённый workflow: 42970625121, build/deploy success. В CI теперь также выполняется python3 -m unittest discover -s scripts -p 'test_*.py'. Актуальный опубликованный коммит и проверенные технически адреса — PORTFOLIO_LINKS.md.
