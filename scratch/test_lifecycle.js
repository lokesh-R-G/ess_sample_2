const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  const logs = [];
  page.on('console', msg => {
    if (msg.text().includes('[AdminDashboard]') || msg.text().includes('[AreaChart]') || msg.text().includes('[DonutChart]') || msg.type() === 'error') {
      logs.push(`${msg.type().toUpperCase()} - ${msg.text()}`);
    }
  });
  
  page.on('pageerror', err => {
    logs.push(`PAGE ERROR - ${err.toString()}`);
  });

  try {
    // Navigate to root to set local storage
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2', timeout: 10000 });
    await page.evaluate(() => { 
        localStorage.setItem('ess_auth_token', 'dummy'); 
        localStorage.setItem('ess_auth_user', JSON.stringify({"id":"1", "role":"Admin"})); 
    });
    
    // Navigate to admin
    await page.goto('http://localhost:5173/admin', { waitUntil: 'networkidle2', timeout: 10000 });
    await new Promise(r => setTimeout(r, 3000));
    console.log(logs.join('\n'));
  } catch (e) {
    console.log("Error running puppeteer:");
    console.log(e);
    console.log(logs.join('\n'));
  } finally {
    await browser.close();
  }
})();
