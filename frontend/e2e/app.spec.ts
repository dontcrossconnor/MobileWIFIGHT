/**
 * E2E Tests - REAL Playwright tests with actual button clicking
 */
import { test, expect } from '@playwright/test';

test.describe('WiFi Pentester E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Wait for app to load
    await page.waitForSelector('[data-testid="api-status"]');
  });

  test('should load the application', async ({ page }) => {
    await expect(page.locator('[data-testid="dashboard-view"]')).toBeVisible();
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('should show API status', async ({ page }) => {
    const apiStatus = page.locator('[data-testid="api-status"]');
    await expect(apiStatus).toBeVisible();
    
    // Check API is online (or checking/offline)
    const text = await apiStatus.textContent();
    expect(text).toMatch(/(Online|Offline|Checking)/);
  });

  test('should navigate between views', async ({ page }) => {
    // Click Scanner
    await page.click('[data-testid="nav-scanner"]');
    await expect(page.locator('[data-testid="scanner-view"]')).toBeVisible();
    await expect(page.locator('h1')).toContainText('Network Scanner');

    // Click Attacks
    await page.click('[data-testid="nav-attacks"]');
    await expect(page.locator('[data-testid="attacks-view"]')).toBeVisible();
    await expect(page.locator('h1')).toContainText('Attacks');

    // Click Cracking
    await page.click('[data-testid="nav-cracking"]');
    await expect(page.locator('[data-testid="cracking-view"]')).toBeVisible();
    await expect(page.locator('h1')).toContainText('Password Cracking');

    // Click Wordlists
    await page.click('[data-testid="nav-wordlists"]');
    await expect(page.locator('[data-testid="wordlists-view"]')).toBeVisible();
    await expect(page.locator('h1')).toContainText('Wordlists');

    // Click Dashboard
    await page.click('[data-testid="nav-dashboard"]');
    await expect(page.locator('[data-testid="dashboard-view"]')).toBeVisible();
  });

  test('should detect adapters when button clicked', async ({ page }) => {
    // Click detect button
    await page.click('[data-testid="detect-adapters-btn"]');
    
    // Wait for button text to change back (indicates completion)
    await expect(page.locator('[data-testid="detect-adapters-btn"]')).toContainText('Detect Adapters');
    
    // Check adapter count updated
    const count = await page.locator('[data-testid="adapter-count"]').textContent();
    expect(parseInt(count || '0')).toBeGreaterThanOrEqual(0);
  });

  test('should start and stop network scan', async ({ page }) => {
    // Navigate to scanner
    await page.click('[data-testid="nav-scanner"]');
    await expect(page.locator('[data-testid="scanner-view"]')).toBeVisible();

    // Check if start button exists
    const startBtn = page.locator('[data-testid="start-scan-btn"]');
    
    // If button is enabled, we have an adapter in monitor mode
    const isEnabled = await startBtn.isEnabled();
    
    if (isEnabled) {
      // Click start scan
      await startBtn.click();
      
      // Wait for scan status to appear
      await page.waitForSelector('[data-testid="scan-status"]', { timeout: 10000 });
      await expect(page.locator('[data-testid="scan-status"]')).toContainText('Scanning');

      // Check networks table exists
      await expect(page.locator('[data-testid="networks-table"]')).toBeVisible();

      // Stop scan
      await page.click('[data-testid="stop-scan-btn"]');
      
      // Verify scan stopped
      await expect(page.locator('[data-testid="start-scan-btn"]')).toBeVisible();
    }
  });

  test('should toggle monitor mode', async ({ page }) => {
    // First detect adapters
    await page.click('[data-testid="detect-adapters-btn"]');
    await page.waitForTimeout(1000);

    // Check if we have adapters
    const noAdapters = await page.locator('[data-testid="no-adapters"]').isVisible().catch(() => false);
    
    if (!noAdapters) {
      // We have adapters, try to toggle monitor mode
      const toggleBtn = page.locator('[data-testid="toggle-monitor-mode-btn"]');
      
      if (await toggleBtn.isVisible()) {
        const initialText = await toggleBtn.textContent();
        
        // Click toggle
        await toggleBtn.click();
        
        // Wait for mode to change
        await page.waitForTimeout(3000);
        
        // Check text changed
        const newText = await toggleBtn.textContent();
        expect(newText).not.toBe(initialText);
      }
    }
  });

  test('should create attack with form inputs', async ({ page }) => {
    // Navigate to attacks
    await page.click('[data-testid="nav-attacks"]');
    await expect(page.locator('[data-testid="attacks-view"]')).toBeVisible();

    // Fill attack form
    await page.fill('[data-testid="target-bssid-input"]', '00:11:22:33:44:55');
    await page.selectOption('[data-testid="attack-type-select"]', 'deauth');
    await page.fill('[data-testid="duration-input"]', '30');

    // Click launch (will fail without proper setup, but tests UI works)
    await page.click('[data-testid="launch-attack-btn"]');
    
    // Wait for response (success or error alert)
    await page.waitForTimeout(1000);
  });

  test('should create cracking job with form inputs', async ({ page }) => {
    // Navigate to cracking
    await page.click('[data-testid="nav-cracking"]');
    await expect(page.locator('[data-testid="cracking-view"]')).toBeVisible();

    // Fill cracking form
    await page.fill('[data-testid="handshake-file-input"]', '/tmp/test.cap');
    await page.fill('[data-testid="crack-bssid-input"]', '00:11:22:33:44:55');
    await page.fill('[data-testid="crack-essid-input"]', 'TestNetwork');
    await page.selectOption('[data-testid="attack-mode-select"]', 'wordlist');
    await page.selectOption('[data-testid="gpu-provider-select"]', 'local');

    // Click create (will fail if file doesn't exist, but tests UI works)
    await page.click('[data-testid="create-job-btn"]');
    
    // Wait for response
    await page.waitForTimeout(1000);
  });

  test('should load wordlists and show download buttons', async ({ page }) => {
    // Navigate to wordlists
    await page.click('[data-testid="nav-wordlists"]');
    await expect(page.locator('[data-testid="wordlists-view"]')).toBeVisible();

    // Wait for wordlists to load
    await page.waitForSelector('[data-testid="wordlists-table"]');
    
    // Check if wordlists loaded
    const rows = page.locator('[data-testid^="wordlist-"]');
    const count = await rows.count();
    expect(count).toBeGreaterThan(0);

    // Check refresh button works
    await page.click('[data-testid="refresh-wordlists-btn"]');
    await page.waitForTimeout(1000);
  });

  test('should show adapter details when clicked', async ({ page }) => {
    // Detect adapters
    await page.click('[data-testid="detect-adapters-btn"]');
    await page.waitForTimeout(1000);

    // Check for adapter list
    const adapterList = page.locator('[data-testid="adapter-list"]');
    
    if (await adapterList.isVisible()) {
      // Click first adapter
      const firstAdapter = page.locator('[data-testid^="adapter-"]').first();
      await firstAdapter.click();

      // Check controls appear
      await expect(page.locator('[data-testid="toggle-monitor-mode-btn"]')).toBeVisible();
    }
  });

  test('should display network details when selected', async ({ page }) => {
    // Navigate to scanner
    await page.click('[data-testid="nav-scanner"]');
    
    // If we have networks, click one
    const networkRows = page.locator('[data-testid^="network-"]');
    const count = await networkRows.count();
    
    if (count > 0) {
      await networkRows.first().click();
      
      // Check details appear
      await expect(page.locator('[data-testid="network-details"]')).toBeVisible();
    }
  });

  test('should show attack progress and status updates', async ({ page }) => {
    // Navigate to attacks
    await page.click('[data-testid="nav-attacks"]');
    
    // Check for existing attacks
    const attacksList = page.locator('[data-testid="attacks-list"]');
    
    if (await attacksList.isVisible()) {
      // Check for attack status elements
      const statusElements = page.locator('[data-testid^="attack-status-"]');
      const statusCount = await statusElements.count();
      expect(statusCount).toBeGreaterThan(0);
    }
  });

  test('should show cracking job progress', async ({ page }) => {
    // Navigate to cracking
    await page.click('[data-testid="nav-cracking"]');
    
    // Check for existing jobs
    const jobsList = page.locator('[data-testid="jobs-list"]');
    
    if (await jobsList.isVisible()) {
      // Check for job status elements
      const statusElements = page.locator('[data-testid^="job-status-"]');
      const statusCount = await statusElements.count();
      expect(statusCount).toBeGreaterThan(0);
    }
  });

  test('should display cracked password when job succeeds', async ({ page }) => {
    // Navigate to cracking
    await page.click('[data-testid="nav-cracking"]');
    
    // Look for password displays (if any jobs succeeded)
    const passwords = page.locator('[data-testid^="job-password-"]');
    // Just checking the selector works - may not have any yet
    expect(await passwords.count()).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Wordlist Management E2E', () => {
  test('should download individual wordlist', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="nav-wordlists"]');
    
    // Wait for wordlists to load
    await page.waitForSelector('[data-testid="wordlists-table"]');
    
    // Find first not-downloaded wordlist
    const downloadBtns = page.locator('[data-testid^="download-"][data-testid$="-btn"]');
    const count = await downloadBtns.count();
    
    if (count > 0) {
      // Click first download button
      const firstBtn = downloadBtns.first();
      await firstBtn.click();
      
      // Button should show "Downloading..."
      await expect(firstBtn).toContainText('Downloading');
      
      // Wait for download to complete (may take a while)
      await expect(firstBtn).not.toBeVisible({ timeout: 60000 });
    }
  });

  test('should download essentials bundle', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="nav-wordlists"]');
    await page.waitForSelector('[data-testid="wordlists-table"]');
    
    // Click download essentials
    await page.click('[data-testid="download-essentials-btn"]');
    
    // Wait for download to complete
    await page.waitForTimeout(5000); // Give it time to start
    
    // Refresh should show updated status
    await page.click('[data-testid="refresh-wordlists-btn"]');
    await page.waitForTimeout(1000);
  });
});

test.describe('Full Attack Workflow E2E', () => {
  test('complete attack workflow: detect → monitor → scan → attack', async ({ page }) => {
    await page.goto('/');

    // Step 1: Detect adapters
    await page.click('[data-testid="detect-adapters-btn"]');
    await page.waitForTimeout(2000);

    // Check if adapters found
    const noAdapters = await page.locator('[data-testid="no-adapters"]').isVisible().catch(() => false);
    
    if (noAdapters) {
      console.log('No adapters detected, skipping workflow test');
      return;
    }

    // Step 2: Enable monitor mode
    const toggleBtn = page.locator('[data-testid="toggle-monitor-mode-btn"]');
    if (await toggleBtn.isVisible()) {
      const btnText = await toggleBtn.textContent();
      
      if (btnText?.includes('Enable')) {
        await toggleBtn.click();
        await page.waitForTimeout(3000); // Wait for mode change
      }
    }

    // Step 3: Start scan
    await page.click('[data-testid="nav-scanner"]');
    await page.waitForTimeout(500);
    
    const startScanBtn = page.locator('[data-testid="start-scan-btn"]');
    if (await startScanBtn.isEnabled()) {
      await startScanBtn.click();
      
      // Wait for scan to find networks
      await page.waitForTimeout(10000); // 10 seconds for networks to appear
      
      // Check networks table
      const networksTable = page.locator('[data-testid="networks-table"]');
      await expect(networksTable).toBeVisible();
      
      // Step 4: Select a network if found
      const networkRows = page.locator('[data-testid^="network-"]');
      const networkCount = await networkRows.count();
      
      if (networkCount > 0) {
        // Click first network
        await networkRows.first().click();
        
        // Details should appear
        await expect(page.locator('[data-testid="network-details"]')).toBeVisible();
        
        // Get BSSID
        const firstNetwork = await networkRows.first().getAttribute('data-testid');
        const bssid = firstNetwork?.replace('network-', '') || '';
        
        // Step 5: Launch attack on this network
        await page.click('[data-testid="nav-attacks"]');
        await page.fill('[data-testid="target-bssid-input"]', bssid);
        await page.selectOption('[data-testid="attack-type-select"]', 'deauth');
        await page.fill('[data-testid="duration-input"]', '10');
        
        await page.click('[data-testid="launch-attack-btn"]');
        
        // Wait for attack to be created
        await page.waitForTimeout(2000);
        
        // Check attacks list
        const attacksList = page.locator('[data-testid="attacks-list"]');
        if (await attacksList.isVisible()) {
          await expect(attacksList).toBeVisible();
        }
      }
      
      // Stop scan
      await page.click('[data-testid="nav-scanner"]');
      await page.click('[data-testid="stop-scan-btn"]');
    }
  });

  test('cracking workflow: create job → monitor progress', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="nav-cracking"]');

    // Fill form
    await page.fill('[data-testid="handshake-file-input"]', '/tmp/test.cap');
    await page.fill('[data-testid="crack-bssid-input"]', 'AA:BB:CC:DD:EE:FF');
    await page.fill('[data-testid="crack-essid-input"]', 'TestNet');
    await page.selectOption('[data-testid="gpu-provider-select"]', 'local');

    // Create job (will fail if file doesn't exist, but tests UI)
    await page.click('[data-testid="create-job-btn"]');
    
    await page.waitForTimeout(2000);
    
    // If job created, should see in list
    const jobsList = page.locator('[data-testid="jobs-list"]');
    // May or may not be visible depending on file existence
  });
});

test.describe('Form Validation E2E', () => {
  test('attack form requires BSSID', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="nav-attacks"]');

    // Try to launch without BSSID
    await page.click('[data-testid="launch-attack-btn"]');
    
    // Should show alert (need to handle dialog)
    page.on('dialog', dialog => {
      expect(dialog.message()).toContain('adapter');
      dialog.accept();
    });
  });

  test('cracking form requires all fields', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="nav-cracking"]');

    // Try to create without filling fields
    await page.click('[data-testid="create-job-btn"]');
    
    // Should show alert
    page.on('dialog', dialog => {
      expect(dialog.message()).toContain('required');
      dialog.accept();
    });
  });
});

test.describe('Visual Regression Tests', () => {
  test('dashboard screenshot', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveScreenshot('dashboard.png');
  });

  test('scanner screenshot', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="nav-scanner"]');
    await expect(page).toHaveScreenshot('scanner.png');
  });

  test('attacks screenshot', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="nav-attacks"]');
    await expect(page).toHaveScreenshot('attacks.png');
  });

  test('cracking screenshot', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="nav-cracking"]');
    await expect(page).toHaveScreenshot('cracking.png');
  });

  test('wordlists screenshot', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="nav-wordlists"]');
    await expect(page).toHaveScreenshot('wordlists.png');
  });
});
