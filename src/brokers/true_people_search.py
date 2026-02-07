from src.brokers.base import BaseBroker
from src.models.database import User
from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)

class TruePeopleSearch(BaseBroker):
    def __init__(self):
        super().__init__(name="TruePeopleSearch", domain="truepeoplesearch.com")
        self.opt_out_url = f"https://www.{self.domain}/removal"

    async def submit_opt_out(self, user: User):
        async with async_playwright() as p:
            # TruePeopleSearch often blocks headless browsers, so we use a realistic UA
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                logger.info(f"Navigating to {self.opt_out_url}")
                await page.goto(self.opt_out_url)
                
                # 1. Agree to terms and enter email
                await page.fill("input#Email", user.email)
                await page.check("input#TermsOfService")
                # CAPTCHA is usually present here. This will likely fail in fully automated mode 
                # unless a solver is used or it's a "soft" check.
                await page.click("button#btnSubmit")
                
                await page.wait_for_timeout(2000)
                
                # 2. Search for the record to remove
                # After email submission, it usually asks to search for the record
                await page.fill("input#Name", user.full_name)
                if user.city and user.state:
                    await page.fill("input#CityStateZip", f"{user.city}, {user.state}")
                await page.click("button#btnSearch")
                
                await page.wait_for_timeout(3000)
                
                # 3. Click "View Details" then "Remove This Record"
                view_details = page.locator("a:has-text('View Details')").first
                if await view_details.count() > 0:
                    await view_details.click()
                    await page.wait_for_timeout(2000)
                    
                    remove_btn = page.locator("button:has-text('Remove This Record')")
                    if await remove_btn.count() > 0:
                        await remove_btn.click()
                        return {"status": "pending", "message": "Removal request sent. Verification email should follow."}
                
                return {"status": "completed", "message": "No matching record found to remove."}

            except Exception as e:
                logger.error(f"Error during TruePeopleSearch opt-out: {str(e)}")
                return {"status": "failed", "error": str(e)}
            finally:
                await browser.close()

    async def check_status(self, external_id: str):
        return "pending"
