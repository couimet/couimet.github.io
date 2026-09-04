import { MessageCode } from '../src/i18n/messageCodes.js';
import { format, getMessages, setLocale } from '../src/i18n/supportedLocales.js';
import { renderPreview, TEMPLATES } from '../src/templates.js';

import { afterEach, beforeEach, describe, expect, it } from 'vitest';

describe('TEMPLATES', () => {
  it('has 3 templates', () => {
    expect(TEMPLATES).toHaveLength(3);
  });

  it('each template has a unique registry-backed 2-char base62 shareId', () => {
    const ids = TEMPLATES.map((t) => t.shareId);
    expect(new Set(ids).size).toBe(TEMPLATES.length);
    for (const id of ids) {
      expect(id).toMatch(/^[0-9A-Za-z]{2}$/);
    }
  });

  it('each template pins a per-locale share ID distinct from its bare shareId', () => {
    for (const t of TEMPLATES) {
      expect(Object.keys(t.pinnedShareIds).sort()).toEqual(['en', 'fr']);
      for (const locale of ['en', 'fr']) {
        const pinned = t.pinnedShareIds[locale];
        expect(pinned, `${t.id} ${locale} pinned id`).toMatch(/^[0-9A-Za-z]{2}$/);
        expect(pinned, `${t.id} ${locale} pinned id differs from bare`).not.toBe(t.shareId);
      }
    }
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
      const result = format(getMessages()[t.messageCode], {
        recipientName: 'Alice',
        roleUrl: 'https://example.com/job',
        careerUrl: 'https://my-career.example.com',
        resumeUrl: 'https://my-resume.example.com',
      });
      expect(result).toEqual(
        'Hi Alice!\n\n' +
          "I came across https://example.com/job and I believe I'd be a good fit for the role.\n\n" +
          'Background: https://my-career.example.com\nRésumé: https://my-resume.example.com\n\n' +
          'Are you available to chat?',
      );
    });
  });

  describe('cold-reachout', () => {
    it('renders with recipient name, company, and role URL', () => {
      const t = TEMPLATES.find((t) => t.id === 'cold-reachout');
      const result = format(getMessages()[t.messageCode], {
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
          'Background: https://my-career.example.com\nRésumé: https://my-resume.example.com\n\n' +
          'Are you available to chat?',
      );
    });
  });

  describe('mutual-intro', () => {
    it('renders with all fields including pronoun', () => {
      const t = TEMPLATES.find((t) => t.id === 'mutual-intro');
      const result = format(getMessages()[t.messageCode], {
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
          'Background: https://my-career.example.com\nRésumé: https://my-resume.example.com\n\n' +
          'Thanks in advance!',
      );
    });

    it('returns an empty string when the message body cannot be rendered', () => {
      const brokenTemplate = { ...TEMPLATES[0], messageCode: 'UNKNOWN_CODE' };
      expect(renderPreview(brokenTemplate, {}, getMessages())).toBe('');
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

      const renderWithPronoun = (pronoun) => renderPreview(t, { ...base, pronoun }, getMessages());

      expect(renderWithPronoun('him')).toContain('introducing me to him');
      expect(renderWithPronoun('her')).toContain('introducing me to her');
      expect(renderWithPronoun('them')).toContain('introducing me to them');
    });
  });

  describe('French messages', () => {
    beforeEach(() => setLocale('fr'));
    afterEach(() => setLocale('en'));

    it('renders the direct-application message in French', () => {
      const t = TEMPLATES.find((t) => t.id === 'direct-application');
      const result = format(getMessages()[t.messageCode], {
        recipientName: 'Alice',
        roleUrl: 'https://example.com/job',
        careerUrl: 'https://my-career.example.com',
        resumeUrl: 'https://my-resume.example.com',
      });
      expect(result).toContain("J'ai trouvé https://example.com/job et je pense que ce poste correspondrait bien à mon profil");
      expect(result).toContain('Disponible pour en discuter ?');
    });

    it('renders the cold-reachout message in French', () => {
      const t = TEMPLATES.find((t) => t.id === 'cold-reachout');
      const result = format(getMessages()[t.messageCode], {
        recipientName: 'Bob',
        companyName: 'Acme Corp',
        roleUrl: 'https://example.com/job2',
        careerUrl: 'https://my-career.example.com',
        resumeUrl: 'https://my-resume.example.com',
      });
      expect(result).toContain('Je contacte des personnes chez Acme Corp');
      expect(result).toContain('Disponible pour en discuter ?');
    });

    it('renders the mutual-intro message in French', () => {
      const t = TEMPLATES.find((t) => t.id === 'mutual-intro');
      const msgs = getMessages();
      const result = format(msgs[t.messageCode], {
        recipientName: 'Carol',
        targetName: 'Dave',
        targetLinkedInUrl: 'https://linkedin.com/in/dave',
        companyName: 'Beta Inc',
        roleUrl: 'https://example.com/job3',
        pronoun: msgs[MessageCode.PRONOUN_HIM],
        careerUrl: 'https://my-career.example.com',
        resumeUrl: 'https://my-resume.example.com',
      });
      expect(result).toContain('Je vois que vous êtes en contact avec Dave (https://linkedin.com/in/dave)');
      expect(result).toContain("Seriez-vous à l'aise de me présenter à lui");
      expect(result).toContain('Parcours : https://my-career.example.com');
    });

    it('maps pronoun values to French', () => {
      const t = TEMPLATES.find((t) => t.id === 'mutual-intro');
      const msgs = getMessages();
      const base = {
        recipientName: 'Grace',
        targetName: 'Heidi',
        targetLinkedInUrl: 'https://linkedin.com/in/heidi',
        companyName: 'Delta Inc',
        roleUrl: 'https://example.com/job5',
        careerUrl: 'https://my-career.example.com',
        resumeUrl: 'https://my-resume.example.com',
      };

      const renderWithPronoun = (pronoun) => renderPreview(t, { ...base, pronoun }, msgs);

      expect(msgs[MessageCode.PRONOUN_HIM]).toBe('lui');
      expect(msgs[MessageCode.PRONOUN_HER]).toBe('elle');
      expect(msgs[MessageCode.PRONOUN_THEM]).toBe('eux');

      expect(renderWithPronoun('him')).toContain('me présenter à lui');
      expect(renderWithPronoun('her')).toContain('me présenter à elle');
      expect(renderWithPronoun('them')).toContain('me présenter à eux');
    });
  });
});
