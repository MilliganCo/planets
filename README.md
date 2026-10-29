# ASCII-симулятор планет

> Public source preview: see [PUBLICATION.md](PUBLICATION.md) for actual checks, known failures and runtime limits.

Десктопная "песочница" N-body гравитации с ASCII-графикой.

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python app.py
```

## Управление

### Базовые хоткеи
- `Space` — пауза/пуск
- `[` `]` — zoom −/+
- `-` `=` — time_scale −/+
- `C` — центрировать камеру на выбранном теле
- `Tab` — переключить выбранное тело
- `T` — toggle следов (вкл/выкл)
- `Backspace` — очистить следы
- `R` — reset (заново пресет)
- `H` — подсказки

### Добавление тел
- `1-4` — выбор типа тела (астероид, планета, гигант, звезда)
- ЛКМ — клик и перетаскивание для создания тела с заданной скоростью
- `M` / `Shift+M` — увеличить/уменьшить массу текущего типа
- `Delete` — удалить выбранное тело
- `F` — зафиксировать выбранное тело

### Orbit Builder
- `O` — включить Orbit Builder (автоматические круговые орбиты)
- `Shift+O` — сменить направление орбиты

### Пресеты
- `F1-F5` — загрузить пресет

### Дополнительно
- `K` — toggle коллизий (вкл/выкл)



## Public source status — 2026-10-29

See [PUBLICATION.md](PUBLICATION.md) for the current verification scope, prototype limitations and runtime boundaries. Earlier audit checklists describe historical work.
