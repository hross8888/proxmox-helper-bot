from aiogram.utils.keyboard import InlineKeyboardBuilder


def arrange_keyboard(
        builder: InlineKeyboardBuilder,
        total_buttons: int | None = None,
        *,
        per_row: int = 4,
        add_back: bool = True,
) -> InlineKeyboardBuilder:
    """
    Универсальный помощник для красивого выравнивания клавиатуры.

    :param builder: InlineKeyboardBuilder, в котором уже добавлены кнопки
    :param total_buttons: общее количество "основных" кнопок (без учёта кнопки "Назад")
                          если None — считается по текущим builder.buttons
    :param per_row: количество кнопок в каждом ряду
    :param add_back: если True — последняя строка будет отдельной (для "Назад")
    :return: InlineKeyboardBuilder с отформатированными рядами
    """
    buttons = list(builder.buttons)
    if total_buttons is None:
        total_buttons = len(buttons) - (1 if add_back else 0)

    full_rows, remainder = divmod(total_buttons, per_row)
    pattern: list[int] = [per_row] * full_rows

    if remainder:
        pattern.append(remainder)
    if add_back:
        pattern.append(1)

    builder.adjust(*pattern)
    return builder