/**
 * Groq AI Service for TendAlert
 * Free, fast AI inference - alternative to Gemini
 * Uses Mixtral 8x7b for high-quality Swedish language support
 */

import Groq from 'groq-sdk';

class GroqService {
  constructor(apiKey) {
    this.client = new Groq({ apiKey });
    this.model = 'mixtral-8x7b-32768';
  }

  /**
   * Analyze a tender document and detect red flags
   */
  async analyzeTender(tender) {
    const prompt = this.buildAnalysisPrompt(tender);
    
    try {
      const chatCompletion = await this.client.chat.completions.create({
        messages: [
          {
            role: 'system',
            content: 'Du är en erfaren upphandlingskonsult som analyserar svenska offentliga upphandlingar för att hjälpa företag att identifiera risker och möjligheter. Svara ALLTID med endast giltig JSON utan markdown-formatering.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        model: this.model,
        temperature: 0.3,
        max_tokens: 2048,
        response_format: { type: 'json_object' }
      });

      const text = chatCompletion.choices[0]?.message?.content || '';
      return this.parseAnalysisResponse(text);
    } catch (error) {
      console.error('Groq analysis error:', error.message);
      throw new Error(`Analysis failed: ${error.message}`);
    }
  }

  /**
   * Build prompt for tender analysis
   */
  buildAnalysisPrompt(tender) {
    return `ANALYSERA FÖLJANDE UPPHANDLING:

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
   * Parse the Groq response
   */
  parseAnalysisResponse(text) {
    try {
      // Clean the response - remove any markdown or text before/after JSON
      let cleanedText = text.trim();
      
      // Try to extract JSON if there's extra text
      const jsonMatch = cleanedText.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        cleanedText = jsonMatch[0];
      }

      const parsed = JSON.parse(cleanedText);
      
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
        estimated_timeline_weeks: Math.max(1, Math.min(52, parseInt(parsed.estimated_timeline_weeks) || 8)),
        model: this.model,
        provider: 'groq'
      };
    } catch (error) {
      console.error('Parse error:', error.message);
      console.error('Raw response:', text.substring(0, 500));
      throw new Error('Failed to parse Groq response');
    }
  }
}

export default GroqService;
