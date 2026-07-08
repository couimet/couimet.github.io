import { TEMPLATES } from '../src/templates.js';

import { describe, expect, it } from 'vitest';

describe('TEMPLATES', () => {
  it('has 3 templates', () => {
    expect(TEMPLATES).toHaveLength(3);
  });

  it('each template includes careerUrl and resumeUrl in shared fields', () => {
    for (const t of TEMPLATES) {
      const names = t.fields.map((f) => f.name);
      expect(names).toContain('careerUrl');
      expect(names).toContain('resumeUrl');
    }
  });

  describe('direct-application', () => {
    it('renders with recipient name and role URL', () => {
      const t = TEMPLATES.find((t) => t.id === 'direct-application');
      const result = t.render({
        recipientName: 'Alice',
        roleUrl: 'https://example.com/job',
        careerUrl: 'https://my-career.example.com',
        resumeUrl: 'https://my-resume.example.com',
      });
      expect(result).toContain('Hi Alice!');
      expect(result).toContain('https://example.com/job');
      expect(result).toContain('good fit');
      expect(result).toContain('https://my-career.example.com');
      expect(result).toContain('https://my-resume.example.com');
    });
  });

  describe('cold-reachout', () => {
    it('renders with recipient name, company, and role URL', () => {
      const t = TEMPLATES.find((t) => t.id === 'cold-reachout');
      const result = t.render({
        recipientName: 'Bob',
        companyName: 'Acme Corp',
        roleUrl: 'https://example.com/job2',
        careerUrl: 'https://my-career.example.com',
        resumeUrl: 'https://my-resume.example.com',
      });
      expect(result).toContain('Hi Bob!');
      expect(result).toContain('Acme Corp');
      expect(result).toContain('https://example.com/job2');
      expect(result).toContain('Are you available');
    });
  });

  describe('mutual-intro', () => {
    it('renders with all fields including pronoun', () => {
      const t = TEMPLATES.find((t) => t.id === 'mutual-intro');
      const result = t.render({
        recipientName: 'Carol',
        targetName: 'Dave',
        targetLinkedInUrl: 'https://linkedin.com/in/dave',
        companyName: 'Beta Inc',
        roleUrl: 'https://example.com/job3',
        pronoun: 'him',
        careerUrl: 'https://my-career.example.com',
        resumeUrl: 'https://my-resume.example.com',
      });
      expect(result).toContain('Hi Carol!');
      expect(result).toContain('Dave');
      expect(result).toContain('https://linkedin.com/in/dave');
      expect(result).toContain('Beta Inc');
      expect(result).toContain('introducing me to him');
    });

    it('uses their pronoun when selected', () => {
      const t = TEMPLATES.find((t) => t.id === 'mutual-intro');
      const result = t.render({
        recipientName: 'Eve',
        targetName: 'Frank',
        targetLinkedInUrl: 'https://linkedin.com/in/frank',
        companyName: 'Gamma LLC',
        roleUrl: 'https://example.com/job4',
        pronoun: 'her',
        careerUrl: 'https://my-career.example.com',
        resumeUrl: 'https://my-resume.example.com',
      });
      expect(result).toContain('introducing me to her');
    });
  });
});
