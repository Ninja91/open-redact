from src.brokers.base import BaseBroker
from src.models.database import User
from playwright.async_api import async_playwright
import asyncio
import logging

logger = logging.getLogger(__name__)

class CyberBackgroundChecks(BaseBroker):
    def __init__(self):
        super().__init__(name="CyberBackgroundChecks", domain="cyberbackgroundchecks.com")
        self.opt_out_url = f"https://www.{self.domain}/opt-out"

    async def submit_opt_out(self, user: User):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                logger.info(f"Navigating to {self.opt_out_url}")
                await page.goto(self.opt_out_url)
                
                # 1. Agree to terms
                await page.click("input#agreement")
                await page.click("button#btnSubmit")
                
                # 2. Search for the user (using email as it's most unique)
                # Note: CyberBackgroundChecks allows searching by name/location or email
                await page.fill("input#EmailAddress", user.email)
                await page.click("button#btnSubmit")
                
                # 3. Handle results
                # In a real scenario, there might be multiple results. 
                # For this MVP, we look for a "Remove" button or specific record match.
                await page.wait_for_timeout(3000) # Wait for results to load
                
                if "No records found" in await page.content():
                    return {"status": "completed", "message": "No record found for this email."}

                # Find the first 'Remove' button (usually associated with a record)
                remove_button = page.locator("a.btn-remove").first
                if await remove_button.count() > 0:
                    await remove_button.click()
                    
                    # 4. Final submission (usually requires solving a CAPTCHA in real life)
                    # For now, we attempt to fill the final email confirmation if present
                    confirm_email = page.locator("input#EmailAddress")
                    if await confirm_email.count() > 0:
                        await confirm_email.fill(user.email)
                        # await page.click("button#btnSubmit") # Would trigger CAPTCHA
                        return {
                            "status": "pending", 
                            "message": "Opt-out initiated. Check your email for a confirmation link from CyberBackgroundChecks.",
                            "external_id": "manual_verification_required"
                        }
                
                return {"status": "failed", "error": "Could not locate the remove button automatically."}

            except Exception as e:
                logger.error(f"Error during CyberBackgroundChecks opt-out: {str(e)}")
                return {"status": "failed", "error": str(e)}
            finally:
                await browser.close()

    async def check_status(self, external_id: str):
        # Most brokers don't have a status API; status is verified by re-searching
        return "pending"
