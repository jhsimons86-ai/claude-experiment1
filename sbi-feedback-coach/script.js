// SBI Feedback Coach - JavaScript
// This application uses Claude API to analyze and structure feedback

class SBIFeedbackCoach {
    constructor() {
        this.apiKey = localStorage.getItem('claude_api_key');
        this.currentFeedback = null;
        this.structuredData = null;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkApiKey();
    }

    setupEventListeners() {
        // Input section
        document.getElementById('analyze-btn').addEventListener('click', () => this.analyzeFeedback());

        // Structure section
        document.getElementById('generate-btn').addEventListener('click', () => this.generateFeedback());

        // Slider changes
        document.getElementById('tone-slider').addEventListener('change', () => {
            if (this.structuredData) {
                // Auto-show regenerate hint
                this.showRegenerateHint();
            }
        });

        document.getElementById('length-slider').addEventListener('change', () => {
            if (this.structuredData) {
                this.showRegenerateHint();
            }
        });

        // Output section
        document.getElementById('copy-email-btn').addEventListener('click', () => this.copyAsEmail());
        document.getElementById('copy-script-btn').addEventListener('click', () => this.copyAsScript());
        document.getElementById('regenerate-btn').addEventListener('click', () => this.regenerateFeedback());
        document.getElementById('start-over-btn').addEventListener('click', () => this.startOver());

        // API settings
        document.getElementById('settings-btn').addEventListener('click', () => this.showApiSetup());
        document.getElementById('save-api-key-btn').addEventListener('click', () => this.saveApiKey());
        document.getElementById('cancel-api-key-btn').addEventListener('click', () => this.hideApiSetup());

        // Enter key in textarea
        document.getElementById('feedback-input').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.analyzeFeedback();
            }
        });
    }

    checkApiKey() {
        if (!this.apiKey) {
            this.showApiSetup();
        }
    }

    showApiSetup() {
        document.getElementById('api-setup').style.display = 'flex';
    }

    hideApiSetup() {
        document.getElementById('api-setup').style.display = 'none';
    }

    saveApiKey() {
        const key = document.getElementById('api-key-input').value.trim();
        if (key) {
            this.apiKey = key;
            localStorage.setItem('claude_api_key', key);
            this.hideApiSetup();
            document.getElementById('api-key-input').value = '';
            this.showNotification('API key saved successfully!');
        } else {
            alert('Please enter a valid API key');
        }
    }

    async callClaudeAPI(prompt, systemPrompt = '') {
        if (!this.apiKey) {
            this.showApiSetup();
            throw new Error('API key required');
        }

        const response = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': this.apiKey,
                'anthropic-version': '2023-06-01'
            },
            body: JSON.stringify({
                model: 'claude-3-5-sonnet-20241022',
                max_tokens: 2048,
                system: systemPrompt,
                messages: [{
                    role: 'user',
                    content: prompt
                }]
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || 'API request failed');
        }

        const data = await response.json();
        return data.content[0].text;
    }

    async analyzeFeedback() {
        const input = document.getElementById('feedback-input').value.trim();

        if (!input) {
            alert('Please enter some feedback to analyze');
            return;
        }

        this.currentFeedback = input;

        const analyzeBtn = document.getElementById('analyze-btn');
        this.setButtonLoading(analyzeBtn, true);

        try {
            const systemPrompt = `You are an expert feedback coach specializing in the SBI (Situation-Behavior-Impact) framework. Your role is to help people structure their feedback effectively.

The SBI framework consists of:
- Situation: The specific time, place, and context when the behavior occurred
- Behavior: Observable, factual actions (not interpretations or judgments)
- Impact: The concrete effect or consequence of the behavior

Extract these components from the user's feedback and return ONLY a valid JSON object with this exact structure:
{
    "situation": "string describing when/where",
    "behavior": "string describing observable actions only",
    "impact": "string describing the effect/consequence"
}

Important:
- Keep behaviors purely observational (what was seen/heard, not what was assumed)
- Be specific and concrete
- Return ONLY the JSON, no other text`;

            const prompt = `Extract the SBI components from this feedback:\n\n${input}`;

            const response = await this.callClaudeAPI(prompt, systemPrompt);

            // Parse the JSON response
            const jsonMatch = response.match(/\{[\s\S]*\}/);
            if (!jsonMatch) {
                throw new Error('Invalid response format');
            }

            this.structuredData = JSON.parse(jsonMatch[0]);

            // Populate the fields
            document.getElementById('situation-field').value = this.structuredData.situation;
            document.getElementById('behavior-field').value = this.structuredData.behavior;
            document.getElementById('impact-field').value = this.structuredData.impact;

            // Show structure section
            this.showSection('structure-section');

        } catch (error) {
            console.error('Error analyzing feedback:', error);
            alert('Error analyzing feedback: ' + error.message);
        } finally {
            this.setButtonLoading(analyzeBtn, false);
        }
    }

    async generateFeedback() {
        // Get current values from fields (user might have edited them)
        const situation = document.getElementById('situation-field').value.trim();
        const behavior = document.getElementById('behavior-field').value.trim();
        const impact = document.getElementById('impact-field').value.trim();

        if (!situation || !behavior || !impact) {
            alert('Please fill in all SBI fields');
            return;
        }

        const tone = document.getElementById('tone-slider').value;
        const length = document.getElementById('length-slider').value;

        const generateBtn = document.getElementById('generate-btn');
        this.setButtonLoading(generateBtn, true);

        try {
            const toneDescription = this.getToneDescription(tone);
            const lengthDescription = this.getLengthDescription(length);

            const systemPrompt = `You are an expert feedback coach. Generate a professional SBI feedback statement and a clear next step.

Guidelines:
- Use the SBI framework: Situation, Behavior, Impact
- Tone: ${toneDescription}
- Length: ${lengthDescription}
- The SBI statement should be 2-6 well-crafted sentences
- The next step should be a single clear, actionable request or question
- Be specific, constructive, and professional
- Avoid blame or judgment
- Focus on observable facts and their impact

Return your response in this exact JSON format:
{
    "sbi_statement": "The complete feedback statement integrating situation, behavior, and impact",
    "next_step": "A clear ask or next action"
}`;

            const prompt = `Create a feedback statement using these components:

Situation: ${situation}
Behavior: ${behavior}
Impact: ${impact}

Tone level: ${tone}/100 (${toneDescription})
Length level: ${length}/100 (${lengthDescription})`;

            const response = await this.callClaudeAPI(prompt, systemPrompt);

            // Parse the JSON response
            const jsonMatch = response.match(/\{[\s\S]*\}/);
            if (!jsonMatch) {
                throw new Error('Invalid response format');
            }

            const result = JSON.parse(jsonMatch[0]);

            // Display the output
            document.getElementById('sbi-output').textContent = result.sbi_statement;
            document.getElementById('ask-output').textContent = result.next_step;

            // Store for copying
            this.generatedFeedback = result;

            // Show output section
            this.showSection('output-section');

        } catch (error) {
            console.error('Error generating feedback:', error);
            alert('Error generating feedback: ' + error.message);
        } finally {
            this.setButtonLoading(generateBtn, false);
        }
    }

    async regenerateFeedback() {
        // Go back to structure section
        this.showSection('structure-section');

        // Scroll to controls
        document.querySelector('.controls').scrollIntoView({ behavior: 'smooth' });
    }

    getToneDescription(value) {
        if (value < 33) return 'direct and straightforward';
        if (value < 67) return 'balanced and professional';
        return 'supportive and encouraging';
    }

    getLengthDescription(value) {
        if (value < 33) return 'concise and brief (2-3 sentences)';
        if (value < 67) return 'moderate detail (3-4 sentences)';
        return 'detailed and comprehensive (4-6 sentences)';
    }

    showRegenerateHint() {
        const generateBtn = document.getElementById('generate-btn');
        generateBtn.textContent = '🔄 Generate with New Settings';
        setTimeout(() => {
            generateBtn.querySelector('.btn-text').textContent = 'Generate Feedback';
        }, 2000);
    }

    async copyAsEmail() {
        const emailFormat = `Subject: Feedback on Recent Interaction

Hi,

I wanted to share some feedback with you.

${this.generatedFeedback.sbi_statement}

${this.generatedFeedback.next_step}

Thanks for taking the time to read this.

Best regards`;

        await this.copyToClipboard(emailFormat);
        this.showNotification('Copied as email format!');
    }

    async copyAsScript() {
        const scriptFormat = `1:1 Conversation Script
━━━━━━━━━━━━━━━━━━━━━━━

Opening:
"I'd like to share some feedback with you. Do you have a few minutes?"

Feedback:
${this.generatedFeedback.sbi_statement}

Next Step:
${this.generatedFeedback.next_step}

Closing:
"I appreciate you listening. Do you have any thoughts on this?"`;

        await this.copyToClipboard(scriptFormat);
        this.showNotification('Copied as 1:1 script!');
    }

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
        } catch (error) {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    }

    showNotification(message) {
        const notification = document.getElementById('copy-notification');
        notification.textContent = message;
        notification.style.display = 'block';

        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }

    showSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.style.display = 'none';
        });

        // Show the requested section
        document.getElementById(sectionId).style.display = 'block';

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    setButtonLoading(button, isLoading) {
        const btnText = button.querySelector('.btn-text');
        const btnLoader = button.querySelector('.btn-loader');

        if (isLoading) {
            btnText.style.display = 'none';
            btnLoader.style.display = 'flex';
            button.disabled = true;
        } else {
            btnText.style.display = 'block';
            btnLoader.style.display = 'none';
            button.disabled = false;
        }
    }

    startOver() {
        // Reset all fields
        document.getElementById('feedback-input').value = '';
        document.getElementById('situation-field').value = '';
        document.getElementById('behavior-field').value = '';
        document.getElementById('impact-field').value = '';
        document.getElementById('tone-slider').value = 50;
        document.getElementById('length-slider').value = 50;

        // Reset data
        this.currentFeedback = null;
        this.structuredData = null;
        this.generatedFeedback = null;

        // Show input section
        this.showSection('input-section');
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new SBIFeedbackCoach();
});
