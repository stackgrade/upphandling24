/**
 * Gemini AI Service for TendAlert
 * Analyzes tender requirements and detects red flags
 */

import { GoogleGenerativeAI } from '@google/generative-ai';

class GeminiService {
  constructor(apiKey) {
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.model = this.genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });
  }

  /**
   * Analyze a tender document and detect red flags
   */
  async analyzeTender(tender) {
    const prompt = this.buildAnalysisPrompt(tender);
    
    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();
      
      return this.parseAnalysisResponse(text);
    } catch (error) {
      console.error('Gemini analysis error:', error.message);
      throw new Error(`Analysis failed: ${error.message}`);
    }
  }

  /**
   * Build prompt for tender analysis
   */
  buildAnalysisPrompt(tender) {
    return `Du är en erfaren upphandlingskonsult som analyserar svenska offentliga upphandlingar för att hjälpa företag att identifiera risker och möjligheter.

ANALYSERA FÖLJANDE UPPHANDLING:

Titel: ${tender.title || 'Ej angiven'}
Beställare: ${tender.buyer || 'Ej angiven'}
Beskrivning: ${tender.description || 'Ej angiven'}
Plats: ${tender.location || 'Ej angiven'}
Uppskattat värde: ${tender.estimated_value ? tender.estimated_value + ' ' + (tender.currency || 'SEK') : 'Ej angivet'}
Deadline: ${tender.deadline || 'Ej angiven'}
Typ: ${tender.contract_type || 'Ej angiven'}

SVAR MED ENDAST JSON I DETTA FORMAT (inga andra texter):
{
  "summary": "Kort sammanfattning av uppdraget i 2-3 meningar",
  "fit_score": 0.0-1.0,
  "fit_explanation": "Varför denna uppdrag passar eller inte passar för en medelstor konsultfirma",
  "red_flags": [
    {
      "severity": "high|medium|low",
      "title": "Rubrik på flaggan",
      "description": "Förklaring av risken",
      "recommendation": "Vad ni bör göra"
    }
  ],
  "requirements_analysis": {
    "technical": "Tekniska krav identifierade",
    "financial": "Ekonomiska krav och garantier",
    "qualification": "Kvalifikationskrav för leverantörer",
    "sustainability": "Hållbarhetskrav och miljökrav"
  },
  "opportunities": ["Möjlighet 1", "Möjlighet 2"],
  "bid_recommendation": "rekommendation|possible|not_recommended",
  "estimated_timeline_weeks": 4-12
}`;
  }

  /**
   * Parse the Gemini response
   */
  parseAnalysisResponse(text) {
    try {
      // Clean the response - remove markdown code blocks if present
      let cleanedText = text.trim();
      if (cleanedText.startsWith('```json')) {
        cleanedText = cleanedText.slice(7);
      } else if (cleanedText.startsWith('```')) {
        cleanedText = cleanedText.slice(3);
      }
      if (cleanedText.endsWith('```')) {
        cleanedText = cleanedText.slice(0, -3);
      }
      
      const parsed = JSON.parse(cleanedText.trim());
      
      // Validate and normalize the response
      return {
        summary: parsed.summary || 'Ingen sammanfattning tillgänglig',
        fit_score: Math.max(0, Math.min(1, parseFloat(parsed.fit_score) || 0.5)),
        fit_explanation: parsed.fit_explanation || '',
        red_flags: Array.isArray(parsed.red_flags) ? parsed.red_flags : [],
        requirements_analysis: {
          technical: parsed.requirements_analysis?.technical || 'Ingen teknisk analys tillgänglig',
          financial: parsed.requirements_analysis?.financial || 'Ingen ekonomisk analys tillgänglig',
          qualification: parsed.requirements_analysis?.qualification || 'Ingen kvalifikationsanalys tillgänglig',
          sustainability: parsed.requirements_analysis?.sustainability || 'Ingen hållbarhetsanalys tillgänglig'
        },
        opportunities: Array.isArray(parsed.opportunities) ? parsed.opportunities : [],
        bid_recommendation: ['rekommendation', 'possible', 'not_recommended'].includes(parsed.bid_recommendation) 
          ? parsed.bid_recommendation 
          : 'possible',
        estimated_timeline_weeks: Math.max(1, Math.min(52, parseInt(parsed.estimated_timeline_weeks) || 8))
      };
    } catch (error) {
      console.error('Parse error:', error.message);
      console.error('Raw response:', text.substring(0, 500));
      throw new Error('Failed to parse Gemini response');
    }
  }
}

export default GeminiService;
