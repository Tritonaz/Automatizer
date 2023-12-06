import pandas

async def loginEmail(prflname, browser):
    page = await browser.newPage()
    df = pandas.read_csv("data/TableName - main.csv")
    email_pass = df.loc[df["id"] == prflname, "email:pass"].values[0]
    email, password = email_pass.split(":") if ":" in email_pass else email_pass.split(" ")
    email_link = "https://" + email.split("@")[1]
    await page.goto(email_link)
    await page.waitForSelector('span.sub-label.i18n.i18n-animation')
    await page.click('span.sub-label.i18n.i18n-animation')
    await page.type('#RainLoopEmail', email)
    await page.type('#RainLoopPassword', password+"\n")
