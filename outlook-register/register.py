from __future__ import annotations

import logging
import random
import time
from typing import Optional

from faker import Faker
from patchright.sync_api import Page

logger = logging.getLogger(__name__)


class RegistrationError(Exception):
    """Raised when registration fails."""


def move_mouse_random(page: Page) -> None:
    """Move mouse to a random point in the viewport to模拟真人光标飘动."""
    size = page.viewport_size or {"width": 1280, "height": 720}
    try:
        x = random.randint(0, size.get("width", 1280))
        y = random.randint(0, size.get("height", 720))
        page.mouse.move(x, y, steps=random.randint(2, 6))
    except Exception:
        # 光标移动失败不影响主流程
        logger.debug("mouse move skipped", exc_info=True)


def wait_before_input(page: Page, min_ms: int = 120, max_ms: int = 480) -> None:
    """在输入前随机等待一小段时间，模拟真人犹豫/思考。"""
    page.wait_for_timeout(random.randint(min_ms, max_ms))


def wait_with_minimum(start_time: float, min_wait_ms: float, page: Page) -> None:
    elapsed_ms = (time.time() - start_time) * 1000
    remaining = max(min_wait_ms - elapsed_ms, 0)
    if remaining > 0:
        page.wait_for_timeout(remaining)


def perform_registration(
    page: Page,
    email: str,
    password: str,
    bot_protection_wait_ms: float,
    max_captcha_retries: int,
) -> bool:
    fake = Faker()
    lastname = fake.last_name()
    firstname = fake.first_name()
    year = str(random.randint(1960, 2005))
    month = str(random.randint(1, 12))
    day = str(random.randint(1, 28))

    try:
        page.goto(
            "https://outlook.live.com/mail/0/?prompt=create_account",
            timeout=20000,
            wait_until="domcontentloaded",
        )
        move_mouse_random(page)
        page.get_by_text("同意并继续").wait_for(timeout=30000)
        start_time = time.time()
        page.wait_for_timeout(0.04 * bot_protection_wait_ms)
        move_mouse_random(page)
        page.get_by_text("同意并继续").click(timeout=30000)
    except Exception:
        logger.warning("IP 质量不佳，无法进入注册界面")
        return False

    try:
        move_mouse_random(page)
        wait_before_input(page)
        page.locator('[aria-label="新建电子邮件"]').type(
            email, delay=0.006 * bot_protection_wait_ms, timeout=10000
        )
        move_mouse_random(page)
        page.locator('[data-testid="primaryButton"]').click(timeout=5000)
        page.wait_for_timeout(0.02 * bot_protection_wait_ms)
        move_mouse_random(page)
        wait_before_input(page)
        page.locator('[type="password"]').type(
            password, delay=0.004 * bot_protection_wait_ms, timeout=10000
        )
        page.wait_for_timeout(0.02 * bot_protection_wait_ms)
        move_mouse_random(page)
        page.locator('[data-testid="primaryButton"]').click(timeout=5000)

        page.wait_for_timeout(0.03 * bot_protection_wait_ms)
        move_mouse_random(page)
        wait_before_input(page)
        page.locator('[name="BirthYear"]').fill(year, timeout=10000)

        try:
            page.wait_for_timeout(0.02 * bot_protection_wait_ms)
            move_mouse_random(page)
            page.locator('[name="BirthMonth"]').select_option(value=month, timeout=1000)
            page.wait_for_timeout(0.05 * bot_protection_wait_ms)
            move_mouse_random(page)
            page.locator('[name="BirthDay"]').select_option(value=day)
        except Exception:
            move_mouse_random(page)
            page.locator('[name="BirthMonth"]').click()
            page.wait_for_timeout(0.02 * bot_protection_wait_ms)
            page.locator(f'[role="option"]:text-is("{month}月")').click()
            page.wait_for_timeout(0.04 * bot_protection_wait_ms)
            move_mouse_random(page)
            page.locator('[name="BirthDay"]').click()
            page.wait_for_timeout(0.03 * bot_protection_wait_ms)
            page.locator(f'[role="option"]:text-is("{day}日")').click()
            move_mouse_random(page)
            page.locator('[data-testid="primaryButton"]').click(timeout=5000)

        move_mouse_random(page)
        wait_before_input(page)
        page.locator('#lastNameInput').type(lastname, delay=0.002 * bot_protection_wait_ms, timeout=10000)
        page.wait_for_timeout(0.02 * bot_protection_wait_ms)
        move_mouse_random(page)
        wait_before_input(page)
        page.locator('#firstNameInput').fill(firstname, timeout=10000)

        wait_with_minimum(start_time, bot_protection_wait_ms, page)

        move_mouse_random(page)
        page.locator('[data-testid="primaryButton"]').click(timeout=5000)
        page.locator('span > [href="https://go.microsoft.com/fwlink/?LinkID=521839"]').wait_for(
            state="detached", timeout=22000
        )

        page.wait_for_timeout(400)

        if page.get_by_text("一些异常活动").count() or page.get_by_text("此站点正在维护，暂时无法使用，请稍后重试。").count() > 0:
            logger.warning("当前 IP 注册频率过快或浏览器异常")
            return False

        if page.locator('iframe#enforcementFrame').count() > 0:
            logger.warning("验证码类型错误，非按压验证码")
            return False

        page.wait_for_event(
            "request",
            lambda req: req.url.startswith("blob:https://iframe.hsprotect.net/"),
            timeout=22000,
        )
        page.wait_for_timeout(800)

        for _ in range(0, max_captcha_retries + 1):
            move_mouse_random(page)
            page.keyboard.press("Enter")
            page.wait_for_timeout(11500)
            move_mouse_random(page)
            page.keyboard.press("Enter")

            try:
                page.wait_for_event(
                    "request",
                    lambda req: req.url.startswith("https://browser.events.data.microsoft.com"),
                    timeout=8000,
                )

                try:
                    page.wait_for_event(
                        "request",
                        lambda req: req.url.startswith(
                            "https://collector-pxzc5j78di.hsprotect.net/assets/js/bundle"
                        ),
                        timeout=1700,
                    )
                    page.wait_for_timeout(2000)
                    continue
                except Exception:
                    if page.get_by_text("一些异常活动").count() or page.get_by_text("此站点正在维护，暂时无法使用，请稍后重试。").count() > 0:
                        logger.warning("通过验证码但 IP 频率过快")
                        return False
                    break
            except Exception:
                page.wait_for_timeout(5000)
                page.keyboard.press("Enter")
                page.wait_for_event(
                    "request",
                    lambda req: req.url.startswith("https://browser.events.data.microsoft.com"),
                    timeout=10000,
                )
                try:
                    page.wait_for_event(
                        "request",
                        lambda req: req.url.startswith(
                            "https://collector-pxzc5j78di.hsprotect.net/assets/js/bundle"
                        ),
                        timeout=4000,
                    )
                except Exception:
                    break
                page.wait_for_timeout(500)
        else:
            raise RegistrationError("验证码超过重试次数")

    except Exception as exc:  # noqa: BLE001
        logger.warning("注册流程失败: %s", exc)
        return False

    return True
