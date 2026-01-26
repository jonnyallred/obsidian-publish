import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"

interface EmailFeedbackOptions {
  email: string
}

const defaultOptions: EmailFeedbackOptions = {
  email: "contact@example.com"
}

export default ((opts?: Partial<EmailFeedbackOptions>) => {
  const options: EmailFeedbackOptions = { ...defaultOptions, ...opts }

  const EmailFeedback: QuartzComponent = ({ fileData }: QuartzComponentProps) => {
    const title = fileData.frontmatter?.title ?? "Feedback"
    const subject = encodeURIComponent(`Re: ${title}`)
    const mailtoLink = `mailto:${options.email}?subject=${subject}`

    return (
      <div class="email-feedback">
        <p>
          <a href={mailtoLink} class="feedback-link">
            ✉️ Send feedback via email
          </a>
        </p>
      </div>
    )
  }

  EmailFeedback.css = `
.email-feedback {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--lightgray);
  font-size: 0.9rem;
  color: var(--darkgray);
}

.email-feedback p {
  margin: 0;
}

.feedback-link {
  color: var(--secondary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.feedback-link:hover {
  color: var(--tertiary);
  text-decoration: underline;
}

@media (max-width: 600px) {
  .email-feedback {
    margin-top: 1.5rem;
    padding-top: 1rem;
  }
}
  `

  return EmailFeedback
}) satisfies QuartzComponentConstructor
