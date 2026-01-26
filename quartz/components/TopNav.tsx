import { pathToRoot } from "../util/path"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"

const TopNav: QuartzComponent = ({ fileData, cfg }: QuartzComponentProps) => {
  const baseDir = pathToRoot(fileData.slug!)
  return (
    <nav class="top-nav">
      <div class="nav-content">
        <a href={baseDir} class="nav-home">{cfg?.pageTitle ?? "Home"}</a>
        <div class="nav-links">
          <a href={baseDir}>Home</a>
          <a href={baseDir + "archive"}>Archive</a>
        </div>
      </div>
    </nav>
  )
}

TopNav.css = `
.top-nav {
  background-color: var(--light);
  border-bottom: 1px solid var(--lightgray);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 1rem 0;
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-home {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--dark);
  text-decoration: none;
}

.nav-home:hover {
  color: var(--secondary);
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-links a {
  color: var(--darkgray);
  text-decoration: none;
  font-size: 0.95rem;
}

.nav-links a:hover {
  color: var(--secondary);
}

@media (max-width: 600px) {
  .nav-content {
    flex-direction: column;
    gap: 0.5rem;
  }

  .nav-links {
    gap: 1rem;
    font-size: 0.85rem;
  }
}
`

export default (() => TopNav) satisfies QuartzComponentConstructor
