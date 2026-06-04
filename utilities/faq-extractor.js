#!/usr/bin/env node

/**
 * FAQ Extractor for 11ty Migration
 * 
 * Reads all FAQ HTML files from static/faqs/
 * Extracts title, slug, and content into src/_data/faqs.json
 * 
 * Usage: node utilities/faq-extractor.js
 */

const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const FAQs_DIR = path.join(__dirname, '../static/faqs');
const OUTPUT_FILE = path.join(__dirname, '../src/_data/faqs.json');

// Category mapping based on filenames and content
const CATEGORY_MAP = {
  'what-does-strategic-lab-partners-do': 'SLP Core',
  'who-does-strategic-lab-partners-work-with': 'SLP Core',
  'what-makes-slp-different-from-other-suppliers': 'SLP Core',
  'what-industries-does-strategic-lab-partners-support': 'SLP Core',
  'what-is-kitting-and-why-does-it-matter': 'SLP Core',
  'what-is-slp\'s-approach-to-innovation': 'SLP Core',
  
  'how-does-slp-design-a-kitting-program': 'Kitting & Manufacturing',
  'how-does-slp-handle-kit-manufacturing-and-assembly': 'Kitting & Manufacturing',
  'how-does-slp-ensure-quality-and-compliance': 'Kitting & Manufacturing',
  'what-are-medical-kitting-fulfillment-services': 'Kitting & Manufacturing',
  'inventory-kitting-definition-how-it-works': 'Kitting & Manufacturing',
  'turnkey-custom-healthcare-kitting-3pl': 'Kitting & Manufacturing',
  'custom-medical-kits-for-healthcare-agencies': 'Kitting & Manufacturing',
  'benefits-of-medical-kitting-for-healthcare-agencies': 'Kitting & Manufacturing',
  'how-medical-kitting-supports-healthcare-providers': 'Kitting & Manufacturing',
  'why-standardized-kits-are-important-for-healthcare-providers': 'Kitting & Manufacturing',
  'how-medical-kitting-streamlines-workflows-for-healthcare-teams': 'Kitting & Manufacturing',
  'how-medical-kitting-reduces-errors-in-healthcare-settings': 'Kitting & Manufacturing',
  'how-medical-kitting-improves-patient-care': 'Kitting & Manufacturing',
  'how-medical-kitting-supports-multi-site-healthcare-organizations': 'Kitting & Manufacturing',
  'how-medical-kitting-supports-regulatory-compliance': 'Kitting & Manufacturing',
  'how-medical-kitting-improves-sample-quality-and-consistency': 'Kitting & Manufacturing',
  'how-medical-kitting-reduces-protocol-deviations': 'Kitting & Manufacturing',
  'importance-of-standardized-kits-in-clinical-trials': 'Kitting & Manufacturing',
  'how-medical-kitting-supports-clinical-trials-and-research': 'Kitting & Manufacturing',
  'benefits-of-outsourcing-medical-kitting-and-fulfillment': 'Kitting & Manufacturing',
  'how-medical-kitting-improves-operational-efficiency': 'Kitting & Manufacturing',
  'difference-between-medical-kitting-and-3pl-fulfillment': 'Kitting & Manufacturing',
  
  'how-does-slp-work-with-3pl-and-deployment': '3PL & Deployment',
  'how-does-slp-manage-inventory-for-clients': '3PL & Deployment',
  'how-does-slp-handle-order-fulfillment': '3PL & Deployment',
  'how-does-slp-support-multi-site-programs': '3PL & Deployment',
  'how-does-slp-handle-returns-and-reverse-logistics': '3PL & Deployment',
  'benefits-of-centralized-medical-logistics': '3PL & Deployment',
  
  'what-is-slp-connect': 'SLP CONNECT™ Digital Oversight',
  'how-does-slp-connect-improve-visibility': 'SLP CONNECT™ Digital Oversight',
  'how-does-slp-connect-integrate-with-kitting-and-3pl': 'SLP CONNECT™ Digital Oversight',
  'how-does-slp-connect-support-program-visibility': 'SLP CONNECT™ Digital Oversight',
  'what-data-does-slp-connect-provide': 'SLP CONNECT™ Digital Oversight',
  'how-does-slp-connect-support-forecasting': 'SLP CONNECT™ Digital Oversight',
  'how-does-slp-connect-support-site-management': 'SLP CONNECT™ Digital Oversight',
  'how-does-slp-connect-support-exception-handling': 'SLP CONNECT™ Digital Oversight',
  'how-slp-connect-integrates-with-kitting-and-fulfillment': 'SLP CONNECT™ Digital Oversight',
  'how-slp-connect-improves-compliance-and-standardization': 'SLP CONNECT™ Digital Oversight',
  'how-slp-connect-supports-scalable-program-growth': 'SLP CONNECT™ Digital Oversight',
  'how-slp-connect-improves-logistics-performance': 'SLP CONNECT™ Digital Oversight',
  'how-slp-connect-reduces-waste-and-inefficiency': 'SLP CONNECT™ Digital Oversight',
  'how-slp-connect-strengthens-program-oversight': 'SLP CONNECT™ Digital Oversight',
  'how-slp-connect-provides-real-time-visibility': 'SLP CONNECT™ Digital Oversight',
  'how-slp-connect-improves-ordering-behavior': 'SLP CONNECT™ Digital Oversight',
  'how-slp-connect-improves-inventory-management': 'SLP CONNECT™ Digital Oversight',
  'slp-connect-nps-transformation': 'SLP CONNECT™ Digital Oversight',
  'slp-connect-financial-control': 'SLP CONNECT™ Digital Oversight',
  'slp-connect-compliance-enforcement': 'SLP CONNECT™ Digital Oversight',
  
  'what-is-your-biggest-concern-with-our-requirements': 'Real Customer Questions (Answered)',
  'how-does-slp-ensure-test-id-accuracy': 'Real Customer Questions (Answered)',
  'how-does-slp-prevent-duplicate-test-ids': 'Real Customer Questions (Answered)',
  'how-does-slp-handle-multi-item-orders': 'Real Customer Questions (Answered)',
  'can-we-edit-or-cancel-orders-in-real-time': 'Real Customer Questions (Answered)',
  'does-slp-offer-saturday-fulfillment': 'Real Customer Questions (Answered)',
  'can-slp-handle-canadian-shipping': 'Real Customer Questions (Answered)',
  'does-slp-offer-inbound-freight-services': 'Real Customer Questions (Answered)',
  'how-does-slp-scale-with-customer-growth': 'Real Customer Questions (Answered)',
  'what-makes-slp-different-from-other-3pls': 'Real Customer Questions (Answered)',
  'what-value-added-services-does-slp-offer': 'Real Customer Questions (Answered)',
  
  'what-is-medical-fulfillment-and-how-does-it-work': 'Medical Fulfillment',
  'benefits-of-outsourcing-medical-fulfillment': 'Medical Fulfillment',
  'how-medical-fulfillment-supports-distributed-healthcare-networks': 'Medical Fulfillment',
  'why-standardized-logistics-are-essential-for-medical-programs': 'Medical Fulfillment',
  'how-medical-fulfillment-improves-accuracy-and-reliability': 'Medical Fulfillment',
  'how-medical-fulfillment-reduces-operational-burden-for-healthcare-organizations': 'Medical Fulfillment',
  'why-inventory-visibility-is-critical-in-medical-fulfillment': 'Medical Fulfillment',
  'how-medical-fulfillment-supports-scalable-healthcare-programs': 'Medical Fulfillment',
  'how-medical-fulfillment-improves-logistics-for-healthcare-programs': 'Medical Fulfillment',
  
  'sample-integrity-genomics-transcriptomics-proteomics-metabolomics': 'Sample Integrity',
  
  'compliance-geographies-regulations': 'Compliance & Regulations',
  
  'slp-integrations-edc-lims-ehr-dtc': 'Integrations',
  
  'decentralized-at-home-collections': 'At-Home Collections',
  
  'benefits-of-sku-consolidation-in-medical-kitting': 'SKU Consolidation & Inventory Strategy',
  'how-many-skus-should-a-medical-kitting-program-have': 'SKU Consolidation & Inventory Strategy',
  'inventory-forecasting-for-medical-kits': 'SKU Consolidation & Inventory Strategy',
};

function extractFAQs() {
  const files = fs.readdirSync(FAQs_DIR).filter(file => file.endsWith('.html') && file !== 'index.html');
  
  const faqs = [];

  files.forEach(file => {
    const filePath = path.join(FAQs_DIR, file);
    const slug = file.replace('.html', '');
    
    try {
      const html = fs.readFileSync(filePath, 'utf-8');
      const dom = new JSDOM(html);
      const doc = dom.window.document;
      
      // Extract title from <h1>
      const h1 = doc.querySelector('h1');
      const title = h1 ? h1.textContent.trim() : slug;
      
      // Extract main content (everything between <h1> and closing </article>)
      const article = doc.querySelector('article');
      if (!article) {
        console.warn(`⚠️  No article element found in ${file}`);
        return;
      }
      
      // Clone the article to manipulate it
      const articleClone = article.cloneNode(true);
      
      // Remove the h1
      const h1InArticle = articleClone.querySelector('h1');
      if (h1InArticle) h1InArticle.remove();
      
      // Get remaining HTML content
      let content = articleClone.innerHTML.trim();
      
      // Clean up the content (remove extra whitespace)
      content = content.replace(/\n\s+/g, '\n').trim();
      
      // Determine category
      const category = CATEGORY_MAP[slug] || 'Uncategorized';
      
      faqs.push({
        slug,
        title,
        category,
        content
      });
      
      console.log(`✓ Extracted: ${title}`);
    } catch (error) {
      console.error(`✗ Error processing ${file}: ${error.message}`);
    }
  });

  // Sort by category, then by title
  faqs.sort((a, b) => {
    if (a.category !== b.category) {
      return a.category.localeCompare(b.category);
    }
    return a.title.localeCompare(b.title);
  });

  // Write to file
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(faqs, null, 2));
  console.log(`\n✅ Extraction complete! ${faqs.length} FAQs extracted to ${OUTPUT_FILE}`);
}

// Run extraction
extractFAQs();
