"""
EPUB Formatter for Kindle
Formats news articles into EPUB format for better Kindle compatibility
"""

from ebooklib import epub
from datetime import datetime
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EpubFormatter:
    def __init__(self):
        self.book = None

    def format_for_kindle(self, nyt_articles):
        """
        Format articles into EPUB format

        Args:
            nyt_articles: List of NYT article dictionaries

        Returns:
            Path to generated EPUB file
        """
        try:
            logger.info(f"Formatting {len(nyt_articles)} NYT Business articles")

            # Create EPUB book
            self.book = epub.EpubBook()

            # Set metadata
            today = datetime.now().strftime('%m-%d-%y')
            self.book.set_identifier(f'daily-news-{today}')
            self.book.set_title(today)
            self.book.set_language('en')
            self.book.add_author('NYT Business')

            # Create chapters
            chapters = []
            spine = ['nav']

            # Add NYT articles
            for i, article in enumerate(nyt_articles, 1):
                chapter = self._create_chapter(
                    article,
                    f'article_{i}',
                    article.get("headline", "Article")
                )
                chapters.append(chapter)
                spine.append(chapter)
                self.book.add_item(chapter)

            # Add table of contents
            self.book.toc = chapters

            # Add navigation files
            self.book.add_item(epub.EpubNcx())
            self.book.add_item(epub.EpubNav())

            # Define spine
            self.book.spine = spine

            # Add CSS
            css = self._get_css()
            nav_css = epub.EpubItem(
                uid="style_nav",
                file_name="style/nav.css",
                media_type="text/css",
                content=css
            )
            self.book.add_item(nav_css)

            # Generate EPUB file
            output_dir = 'output'
            os.makedirs(output_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'{output_dir}/daily_news_{timestamp}.epub'

            epub.write_epub(filename, self.book, {})

            logger.info("Formatting complete")
            return filename

        except Exception as e:
            logger.error(f"Error formatting EPUB: {e}")
            raise

    def _create_chapter(self, article, chapter_id, title):
        """Create an EPUB chapter from an article"""

        headline = article.get('headline', 'No title')
        author = article.get('author', '')
        date = article.get('date', '')
        content = article.get('content', '')
        url = article.get('url', '')

        # Build HTML content
        html_content = f'''
        <html>
        <head>
            <title>{headline}</title>
            <link rel="stylesheet" href="style/nav.css" type="text/css"/>
        </head>
        <body>
            <h1>{headline}</h1>
        '''

        if author:
            html_content += f'<p class="author">By {author}</p>'

        if date:
            html_content += f'<p class="date">{date}</p>'

        html_content += '<div class="content">'

        # Split content into paragraphs
        if content:
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    html_content += f'<p>{para.strip()}</p>\n'

        html_content += '</div>'

        if url:
            html_content += f'<p class="url"><small>Source: <a href="{url}">{url}</a></small></p>'

        html_content += '''
        </body>
        </html>
        '''

        # Create chapter
        chapter = epub.EpubHtml(
            title=title,
            file_name=f'{chapter_id}.xhtml',
            lang='en'
        )
        chapter.content = html_content

        return chapter

    def _get_css(self):
        """Get CSS styles for the EPUB"""
        return '''
        body {
            font-family: Georgia, serif;
            line-height: 1.6;
            margin: 1em;
            color: #000;
        }

        h1 {
            font-size: 1.8em;
            margin-bottom: 0.5em;
            color: #000;
            border-bottom: 2px solid #000;
            padding-bottom: 0.5em;
        }

        .author {
            font-style: italic;
            color: #666;
            margin-bottom: 0.3em;
        }

        .date {
            font-size: 0.9em;
            color: #888;
            margin-bottom: 1em;
        }

        .content {
            text-align: justify;
            margin-top: 1em;
        }

        .content p {
            margin-bottom: 1em;
        }

        .url {
            margin-top: 2em;
            padding-top: 1em;
            border-top: 1px solid #ccc;
            font-size: 0.8em;
            color: #666;
        }

        a {
            color: #0066cc;
            text-decoration: none;
        }
        '''


if __name__ == "__main__":
    # Test the formatter
    test_articles = [
        {
            'headline': 'Test Article',
            'author': 'Test Author',
            'date': '2026-01-09',
            'content': 'This is a test article.\n\nWith multiple paragraphs.',
            'url': 'https://example.com/article'
        }
    ]

    formatter = EpubFormatter()
    filename = formatter.format_for_kindle(test_articles)
    print(f"Test EPUB created: {filename}")
