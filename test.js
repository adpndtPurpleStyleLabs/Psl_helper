const fs = require('fs');
const path = require('path');

process.env.GITHUB_WORKSPACE = './.github'
// Read the template file
const templatePath = path.join(process.env.GITHUB_WORKSPACE, 'email_templates', 'project-update.html');
let htmlTemplate = fs.readFileSync(templatePath, 'utf8');

const context = {}

// Replace template variables
const templateData = {
  projectname: context.payload?.project?.name || 'n/a',
  action: context.payload?.action || 'created',
  actor: context?.actor || 'ashwin',
  timestamp: new date().toisostring(),
  changes: json.stringify(context || {}, null, 2),
  projecturl: `https://github.com/${context?.repo?.owner || 'aditya'}/${context?.repo?.repo || 'psl_helper'}/projects`,
  columnname: context.payload?.project_card?.column_name,
  content: context.payload?.project_card?.note || 'n/a',
  contenturl: context.payload?.project_card?.content_url || '#',
  owner: context.repo?.owner,
  repo: context.repo?.repo
};

// Replace all variables in template
for (const [key, value] of Object.entries(templateData)) {
  htmlTemplate = htmlTemplate.replace(new RegExp("${"+ key +"}", 'g'), value);
}

(async function () {


const response = await fetch('https://api.postmarkapp.com/email', {
  method: 'POST',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    // 'X-Postmark-Server-Token': '${{ secrets.POSTMARK_API_TOKEN }}'
    'X-Postmark-Server-Token': '9bfa1d79-6de5-4aa8-a911-de02cbaf882b'
  },
  body: JSON.stringify({
    "From": "tech@purplestylelabs.com",
    "To": "ashwin.khode@purplestylelabs.com",
    "Subject": `Project Board Update - ${templateData.repo || 'psl_helper'}`,
    "HtmlBody": htmlTemplate,
    "MessageStream": "outbound"
  })
});

if (!response.ok) {
  const error = await response.json();
  core.setFailed(`Failed to send email: ${error.Message}`);
}})()
