from src.brokers.base import BaseBroker
from src.models.database import User
from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)

class OfficialUSA(BaseBroker):
    def __init__(self):
        super().__init__(name="OfficialUSA", domain="officialusa.com")
        self.opt_out_url = "https://www.officialusa.com/opt-out/"

    async def submit_opt_out(self, user: User):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                logger.info(f"Navigating to {self.opt_out_url}")
                await page.goto(self.opt_out_url)
                
                # Fill the search form (OfficialUSA usually requires Name and State)
                names = user.full_name.split(" ")
                first_name = names[0]
                last_name = names[-1] if len(names) > 1 else ""
                
                await page.fill("input[name='fname']", first_name)
                await page.fill("input[name='lname']", last_name)
                if user.state:
                    await page.select_option("select[name='state']", user.state)
                
                await page.click("button[type='submit']")
                await page.wait_for_timeout(3000)
                
                # Look for the removal button in results
                # Also extract findings
                findings = {}
                try:
                    record = page.locator(".result-card, .person-info").first
                    if await record.count() > 0:
                        findings["details"] = await record.inner_text()
                except:
                    pass

                remove_link = page.locator("a:has-text('Remove')").first
                if await remove_link.count() > 0:
                    await remove_link.click()
                    return {
                        "status": "pending", 
                        "message": "Opt-out request submitted. They may send a confirmation email.",
                        "scraped_data": findings
                    }
                
                return {"status": "completed", "message": "No record found on OfficialUSA.", "scraped_data": findings}

            except Exception as e:
                logger.error(f"Error during OfficialUSA opt-out: {str(e)}")
                return {"status": "failed", "error": str(e)}
            finally:
                await browser.close()

    async def check_status(self, external_id: str):
        return "pending"
