import { Date, getDate } from "./Date"
import { QuartzComponentConstructor, QuartzComponentProps } from "./types"
import readingTime from "reading-time"
import { i18n } from "../i18n"

const MetadataSidebar: QuartzComponent = ({ cfg, fileData, displayClass }: QuartzComponentProps) => {
  const text = fileData.text
  const tags = fileData.frontmatter?.tags ?? []

  return (
    <div class={`metadata-sidebar`}>
      {fileData.dates && (
        <div class="metadata-item">
          <span class="metadata-label">Published</span>
          <Date date={getDate(cfg, fileData)!} locale={cfg.locale} />
        </div>
      )}

      {text && (
        <div class="metadata-item">
          <span class="metadata-label">Reading time</span>
          <span class="reading-time">
            {Math.ceil(readingTime(text).minutes)} min
          </span>
        </div>
      )}

      {tags && tags.length > 0 && (
        <div class="metadata-item">
          <span class="metadata-label">Tags</span>
          <div class="tags-list">
            {tags.map((tag: string) => (
              <a href={`/tags/${tag}`} class="tag">
                {tag}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

MetadataSidebar.css = `
.metadata-sidebar {
  font-size: 0.85rem;
  color: var(--darkgray);
  background-color: var(--lightgray);
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

.metadata-item {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metadata-item:last-child {
  margin-bottom: 0;
}

.metadata-label {
  font-weight: 600;
  color: var(--dark);
  text-transform: uppercase;
  font-size: 0.7rem;
  letter-spacing: 0.05em;
}

.reading-time {
  color: var(--darkgray);
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.tag {
  display: inline-block;
  background-color: var(--highlight);
  color: var(--dark);
  padding: 0.25rem 0.6rem;
  border-radius: 0.3rem;
  text-decoration: none;
  font-size: 0.8rem;
  transition: background-color 0.2s;
}

.tag:hover {
  background-color: var(--secondary);
  color: var(--light);
}

@media (max-width: 600px) {
  .metadata-sidebar {
    margin-bottom: 1rem;
    padding: 0.75rem;
  }

  .metadata-item {
    margin-bottom: 0.75rem;
  }
}
`

export default (() => MetadataSidebar) satisfies QuartzComponentConstructor
