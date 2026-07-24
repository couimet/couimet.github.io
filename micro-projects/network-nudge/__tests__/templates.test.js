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
      expect(result).toEqual(
        'Hi Alice!\n\n' +
          "I came across https://example.com/job and I believe I'd be a good fit for the role.\n\n" +
          'My background is at https://my-career.example.com and my latest résumé is at https://my-resume.example.com.\n\n' +
          'Are you available to chat?',
      );
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
      expect(result).toEqual(
        'Hi Bob!\n\n' +
          "I'm connecting with people at Acme Corp for this role:\n" +
          'https://example.com/job2\n\n' +
          'My background is at https://my-career.example.com and my latest résumé is at https://my-resume.example.com.\n\n' +
          'Are you available for a chat?',
      );
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
      expect(result).toEqual(
        'Hi Carol!\n\n' +
          "I saw you're connected with Dave (https://linkedin.com/in/dave).\n\n" +
          "I'm trying to create connections with people at Beta Inc for this role:\n" +
          'https://example.com/job3\n\n' +
          'Would you be comfortable introducing me to him through either email or LinkedIn chat?\n\n' +
          'My background is at https://my-career.example.com and my latest résumé is at https://my-resume.example.com.\n\n' +
          'Thanks in advance!',
      );
    });

    it('produces the correct pronoun in the output', () => {
      const t = TEMPLATES.find((t) => t.id === 'mutual-intro');
      const base = {
        recipientName: 'Grace',
        targetName: 'Heidi',
        targetLinkedInUrl: 'https://linkedin.com/in/heidi',
        companyName: 'Delta Inc',
        roleUrl: 'https://example.com/job5',
        careerUrl: 'https://my-career.example.com',
        resumeUrl: 'https://my-resume.example.com',
      };

      expect(t.render({ ...base, pronoun: 'him' })).toContain('introducing me to him');
      expect(t.render({ ...base, pronoun: 'her' })).toContain('introducing me to her');
      expect(t.render({ ...base, pronoun: 'them' })).toContain('introducing me to them');
    });
  });
});
