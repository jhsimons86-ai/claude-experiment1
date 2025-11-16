# SBI Feedback Coach

An elegant web application that helps you craft effective feedback using the SBI (Situation-Behavior-Impact) framework, powered by Claude AI.

## What is SBI?

The SBI framework is a structured approach to giving feedback that focuses on:

- **Situation**: The specific time, place, and context when something occurred
- **Behavior**: Observable, factual actions (not interpretations or assumptions)
- **Impact**: The concrete effect or consequence of the behavior

## Features

- **Smart Analysis**: Describe your feedback in your own words, and Claude AI extracts the SBI components
- **Structured Editing**: Review and refine the extracted Situation, Behavior, and Impact
- **Customizable Output**: Adjust tone (direct ↔ supportive) and length (concise ↔ detailed) with intuitive sliders
- **Professional Formatting**: Generate polished 2-6 sentence feedback statements
- **Ready-to-Use Templates**: Copy as email or 1:1 conversation script
- **Elegant Interface**: Clean, modern design that's easy to use

## Getting Started

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, Edge)
- A Claude API key from [Anthropic](https://console.anthropic.com/)

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd sbi-feedback-coach
   ```

2. **Open the application**
   - Simply open `index.html` in your web browser
   - Or use a local server:
     ```bash
     # Using Python 3
     python -m http.server 8000

     # Using Node.js
     npx serve
     ```
   - Then navigate to `http://localhost:8000`

3. **Set up your API key**
   - Click the "⚙️ API Settings" button in the footer
   - Enter your Claude API key
   - Your key is stored securely in your browser's local storage

### Getting a Claude API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you won't be able to see it again!)

## How to Use

### Step 1: Describe Your Feedback

In the text area, describe the situation you want to give feedback about in your own words. Be as detailed or brief as you like.

**Example:**
```
My teammate Sarah interrupted me multiple times during yesterday's
client presentation. It made me feel unheard and I think it confused
the client about who was leading the meeting.
```

Click "Analyze Feedback" to proceed.

### Step 2: Review SBI Components

Claude AI will extract and structure your feedback into:
- **Situation**: When and where it happened
- **Behavior**: What observable actions occurred
- **Impact**: What the effect was

You can edit these fields to refine the components.

### Step 3: Customize Your Feedback

Use the sliders to adjust:
- **Tone**: From direct and straightforward to supportive and encouraging
- **Length**: From concise (2-3 sentences) to detailed (4-6 sentences)

Click "Generate Feedback" to create your structured statement.

### Step 4: Use Your Feedback

Review the generated:
- **SBI Statement**: A polished, professional feedback message
- **Next Step**: A clear ask or action item

Copy your feedback as:
- **📧 Email**: Formatted ready to send
- **💬 1:1 Script**: Structured for an in-person conversation

Want to adjust? Click "🔄 Adjust & Regenerate" to go back and change the tone or length.

## Examples

### Input
```
During our team meeting on Monday, Alex took credit for the dashboard
design that I created. The whole team now thinks it was his work, and
I feel like my contribution is invisible.
```

### Generated SBI Statement (Balanced tone, Moderate length)
```
In Monday's team meeting, when we were discussing the new features,
I noticed that you presented the dashboard design as your own work.
I had created that design over the past two weeks, and when credit
wasn't attributed to me, I felt my contribution was overlooked.
This also meant the team doesn't have an accurate understanding of
who worked on what, which could affect future project assignments.
```

### Next Step
```
Could we clarify the authorship with the team in our next meeting,
and discuss how we can better acknowledge individual contributions
going forward?
```

## Privacy & Security

- Your API key is stored only in your browser's local storage
- No data is sent to any server except Claude's API
- All processing happens in your browser and through Claude's secure API
- Your feedback data is not stored or logged anywhere

## Technical Details

### Built With
- Pure HTML, CSS, and JavaScript (no frameworks required)
- Claude API (Sonnet 3.5) for intelligent feedback analysis
- Modern CSS with responsive design
- Local storage for API key management

### Browser Compatibility
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

### API Usage
- Uses Claude 3.5 Sonnet model
- Typically 2 API calls per feedback session:
  1. Initial analysis to extract SBI components
  2. Generation of final feedback statement
- Each call uses approximately 1,000-2,000 tokens

## Troubleshooting

### "API key required" error
- Make sure you've entered your API key in the settings
- Verify your API key is valid and has available credits

### "Invalid response format" error
- This is rare, try clicking the button again
- The AI occasionally formats responses differently

### Feedback seems off-target
- Try providing more context in your initial description
- Edit the SBI fields directly before generating
- Adjust the tone and length sliders

### Copy buttons not working
- Ensure your browser allows clipboard access
- Try clicking the button again
- On some browsers, you may need to manually select and copy

## Cost Estimate

- Each feedback session typically costs $0.01-0.03 USD in API credits
- Based on Claude 3.5 Sonnet pricing as of 2024

## Future Enhancements

- Save feedback history
- Export to different formats (PDF, Word)
- Team feedback templates
- Multi-language support
- Feedback quality scoring

## Support

For issues or questions:
- Check the Troubleshooting section above
- Review [Claude API documentation](https://docs.anthropic.com/)
- Open an issue in this repository

## License

This project is provided as-is for personal and professional use.

## Acknowledgments

- Built with Claude AI
- SBI Framework methodology
- Inspired by best practices in professional feedback

---

**Happy Feedback Coaching!** 🎯
