"""Offline checks; no API calls or credentials needed."""
import unittest
from tools import ResearchTools, citation_warnings, analyze_text
from research_assistant import render_report

class FakeSearch:
    def search(self, **kwargs):
        return {"results": [
            {"url": "https://example.org/a", "title": "Evidence", "content": "Some evidence."},
            {"url": "javascript:alert(1)", "content": "invalid"},
        ]}

class Tests(unittest.TestCase):
    def test_search_budget_and_source_deduplication(self):
        tools = ResearchTools(FakeSearch(), max_searches=2)
        a = tools.search("first")
        b = tools.search("second")
        self.assertEqual(a['sources'][0]['id'], 'S1')
        self.assertEqual(b['sources'][0]['id'], 'S1')
        self.assertEqual(len(tools.sources), 1)
        self.assertIn('error', tools.search('third'))

    def test_search_failure_does_not_leak_exception(self):
        class Broken:
            def search(self, **kwargs):
                raise RuntimeError('secret-key')
        tools = ResearchTools(Broken())
        self.assertNotIn('secret-key', str(tools.search('topic')))
        self.assertEqual(len(tools.warnings), 1)

    def test_unknown_and_missing_citations(self):
        sources = [{'id': 'S1'}]
        self.assertEqual(citation_warnings('Evidence [S1]', sources), [])
        self.assertIn('S9', citation_warnings('Evidence [S9]', sources)[0])
        self.assertTrue(citation_warnings('No citations', sources))

    def test_analysis(self):
        result = analyze_text('Research matters. Research helps!')
        self.assertEqual(result['word_count'], 4)
        self.assertEqual(result['sentence_count'], 2)
        self.assertEqual(result['frequent_terms'][0], ('research', 2))

    def test_report_preserves_sources_and_warnings(self):
        state = {'topic': 'AI', 'summary': 'Summary [S1]', 'review': 'Review',
                 'recommendations': 'Proposal', 'sources': [{'id':'S1', 'title':'Source',
                 'url':'https://example.org', 'retrieved_at':'2026-10-01'}]}
        report = render_report(state, 'test-model', ['Incomplete evidence'])
        self.assertIn('https://example.org', report)
        self.assertIn('Incomplete evidence', report)
        self.assertIn('## Recommendations', report)

if __name__ == '__main__':
    unittest.main()
