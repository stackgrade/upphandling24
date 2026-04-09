/**
 * TendAlert Backend Server
 * Express/Node.js server with Gemini AI analysis endpoint
 */

import express from 'express';
import cors from 'cors';
import { config } from 'dotenv';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import GeminiService from './services/gemini.js';

// Load environment variables
config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Load Swedish tender seed data
const tendersData = JSON.parse(
  readFileSync(join(__dirname, 'data', 'swedish-tenders.json'), 'utf-8')
);

// Initialize Gemini service (lazy - only when needed)
let geminiService = null;
function getGeminiService() {
  if (!geminiService) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      throw new Error('GEMINI_API_KEY not configured');
    }
    geminiService = new GeminiService(apiKey);
  }
  return geminiService;
}

// ============================================
// API ENDPOINTS
// ============================================

/**
 * GET /api/health
 * Health check endpoint
 */
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    gemini_configured: !!process.env.GEMINI_API_KEY,
    tenders_loaded: tendersData.length
  });
});

/**
 * GET /api/tenders
 * List all available Swedish tenders
 */
app.get('/api/tenders', (req, res) => {
  const { region, contract_type, min_value, max_value } = req.query;
  
  let filtered = [...tendersData];
  
  if (region) {
    filtered = filtered.filter(t => 
      t.region.toLowerCase().includes(region.toLowerCase())
    );
  }
  
  if (contract_type) {
    filtered = filtered.filter(t => 
      t.contract_type.toLowerCase().includes(contract_type.toLowerCase())
    );
  }
  
  if (min_value) {
    filtered = filtered.filter(t => t.estimated_value >= parseInt(min_value));
  }
  
  if (max_value) {
    filtered = filtered.filter(t => t.estimated_value <= parseInt(max_value));
  }
  
  res.json({
    count: filtered.length,
    total: tendersData.length,
    tenders: filtered
  });
});

/**
 * GET /api/tenders/:id
 * Get a specific tender by ID
 */
app.get('/api/tenders/:id', (req, res) => {
  const tender = tendersData.find(t => t.id === req.params.id);
  
  if (!tender) {
    return res.status(404).json({
      error: 'Tender not found',
      available_ids: tendersData.map(t => t.id)
    });
  }
  
  res.json(tender);
});

/**
 * POST /api/analyze-tender
 * Analyze a tender using Gemini AI
 * 
 * Request body:
 * {
 *   tender_id: "SE-2026-001" OR
 *   tender: { ...tender object... }
 * }
 */
app.post('/api/analyze-tender', async (req, res) => {
  try {
    const { tender_id, tender: inlineTender } = req.body;
    
    // Get tender data
    let tender;
    if (inlineTender) {
      tender = inlineTender;
    } else if (tender_id) {
      tender = tendersData.find(t => t.id === tender_id);
      if (!tender) {
        return res.status(404).json({
          error: 'Tender not found',
          tender_id,
          available_ids: tendersData.map(t => t.id)
        });
      }
    } else {
      return res.status(400).json({
        error: 'Either tender_id or tender object is required'
      });
    }
    
    // Check if Gemini is configured
    if (!process.env.GEMINI_API_KEY) {
      return res.status(503).json({
        error: 'Gemini API not configured',
        message: 'Set GEMINI_API_KEY environment variable to enable AI analysis',
        mock_available: true
      });
    }
    
    // Perform analysis
    const analysis = await getGeminiService().analyzeTender(tender);
    
    res.json({
      tender_id: tender.id || tender_id,
      tender_title: tender.title,
      analysis,
      analyzed_at: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('Analysis error:', error);
    res.status(500).json({
      error: 'Analysis failed',
      message: error.message
    });
  }
});

/**
 * GET /api/red-flags/:id
 * Get pre-identified red flags for a specific tender
 */
app.get('/api/red-flags/:id', async (req, res) => {
  const tender = tendersData.find(t => t.id === req.params.id);
  
  if (!tender) {
    return res.status(404).json({
      error: 'Tender not found'
    });
  }
  
  // Pre-defined red flag patterns for Swedish tenders
  const redFlags = analyzeRedFlags(tender);
  
  res.json({
    tender_id: tender.id,
    title: tender.title,
    red_flags: redFlags
  });
});

/**
 * Analyze tender for common red flags
 */
function analyzeRedFlags(tender) {
  const flags = [];
  const desc = (tender.description || '').toLowerCase();
  const title = (tender.title || '').toLowerCase();
  
  // Check for very short deadlines (red flag)
  if (tender.deadline) {
    const deadline = new Date(tender.deadline);
    const now = new Date();
    const daysUntilDeadline = (deadline - now) / (1000 * 60 * 60 * 24);
    
    if (daysUntilDeadline < 14) {
      flags.push({
        severity: 'high',
        title: 'Mycket kort anbudsfrist',
        description: `Endast ${Math.round(daysUntilDeadline)} dagar till deadline. Kan tyda på brådska eller strategisk exclusion.`,
        recommendation: 'Begär anstånd eller överväg om tiden räcker för kvalitativ anbud'
      });
    }
  }
  
  // Check for very high value without clear requirements
  if (tender.estimated_value && tender.estimated_value > 100000000) {
    flags.push({
      severity: 'medium',
      title: 'Mycket högt uppskattat värde',
      description: `Värdet ${tender.estimated_value.toLocaleString()} SEK kräver betydande resurser och kapacitet.`,
      recommendation: 'Verifiera att ni har kapacitet och eventuella garantier för denna storlek'
    });
  }
  
  // Check for foreign buyers or cross-border procurement
  if (tender.source && tender.source.includes('TED')) {
    flags.push({
      severity: 'low',
      title: 'EU-direktivupphandling',
      description: 'Upphandlingen följer EU-direktiv och är öppen för utländska anbudsgivare.',
      recommendation: 'Förbered dokumentation för utländska myndigheters granskning'
    });
  }
  
  // Check for construction (often problematic)
  if (tender.contract_type && tender.contract_type.toLowerCase().includes('bygg')) {
    flags.push({
      severity: 'medium',
      title: 'Byggentreprenad',
      description: 'Byggprojekt har ofta hög risk för kostnadsöverdrag och fördröjningar.',
      recommendation: 'Säkerställ noggrann kostnadskalkyl och riskbedömning'
    });
  }
  
  // Check for vague descriptions
  if (desc.length < 100) {
    flags.push({
      severity: 'medium',
      title: 'Vag anbudsbeskrivning',
      description: 'Beskrivningen är mycket kort vilket kan göra det svårt att bedöma om uppdraget passar.',
      recommendation: 'Begär kompletterande information eller gör platsbesök'
    });
  }
  
  return flags;
}

// ============================================
// STATIC FILES (for production)
// ============================================

app.use(express.static(join(__dirname, 'public')));

// ============================================
// ERROR HANDLING
// ============================================

app.use((req, res) => {
  res.status(404).json({
    error: 'Endpoint not found',
    available_endpoints: [
      'GET /api/health',
      'GET /api/tenders',
      'GET /api/tenders/:id',
      'POST /api/analyze-tender',
      'GET /api/red-flags/:id'
    ]
  });
});

app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// ============================================
// START SERVER
// ============================================

app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════╗
║           TendAlert Backend Server                    ║
╠═══════════════════════════════════════════════════════╣
║  Status:     RUNNING                                  ║
║  Port:       ${PORT}                                     ║
║  Tenders:    ${tendersData.length} Swedish tenders loaded              ║
║  Gemini:     ${process.env.GEMINI_API_KEY ? 'CONFIGURED' : 'NOT SET (set GEMINI_API_KEY)'}                          ║
╠═══════════════════════════════════════════════════════╣
║  Endpoints:                                          ║
║  GET  /api/health         - Health check             ║
║  GET  /api/tenders       - List all tenders          ║
║  GET  /api/tenders/:id   - Get specific tender       ║
║  POST /api/analyze-tender - AI analysis with red flags║
║  GET  /api/red-flags/:id - Get red flags            ║
╚═══════════════════════════════════════════════════════╝
  `);
});
