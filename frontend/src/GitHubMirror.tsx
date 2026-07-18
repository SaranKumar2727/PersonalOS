import { useEffect, useState } from 'react'
import { ExternalLink, GitBranch, RefreshCw, Star } from 'lucide-react'

type Repo = {
  id: number
  name: string
  description: string
  language: string
  repository_url: string
  stars: number
  forks: number
  updated_at: string
  deployed_url?: string
}

const API = 'http://127.0.0.1:8000/api/v1'

function storageKey() {
  let user = 'default'
  try {
    const profile = JSON.parse(localStorage.getItem('personal-os-user') || 'null')
    user = profile?.email || profile?.name || user
  } catch {
    // Ignore malformed session data.
  }
  return `personal-os-github-deployments-${localStorage.getItem('personal-os-github-profile') || user}`
}

export default function GitHubMirror() {
  const [repos, setRepos] = useState<Repo[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const sync = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API}/github/repos`)
      const data: Repo[] = await response.json()
      if (!response.ok) throw new Error((data as unknown as { detail: string }).detail)
      const saved = JSON.parse(localStorage.getItem(storageKey()) || '{}')
      setRepos(data.map((repo) => ({ ...repo, deployed_url: saved[repo.id] || '' })))
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not sync GitHub')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void sync()
  }, [])

  const saveDeployment = (repo: Repo, value: string) => {
    const saved = JSON.parse(localStorage.getItem(storageKey()) || '{}')
    saved[repo.id] = value
    localStorage.setItem(storageKey(), JSON.stringify(saved))
    setRepos((current) => current.map((item) => item.id === repo.id ? { ...item, deployed_url: value } : item))
  }

  return <section className="mx-auto max-w-7xl px-5 pt-8 sm:px-9">
    <div className="mb-6 flex items-center justify-between">
      <div>
        <div className="flex items-center gap-2"><GitBranch size={19} className="text-forest" /><h1 className="text-2xl font-bold">GitHub repositories</h1></div>
        <p className="mt-1 text-sm text-muted">Your mirrored public repositories.</p>
      </div>
      <button onClick={sync} className="inline-flex items-center gap-2 rounded-xl bg-ink px-3 py-2 text-xs font-semibold text-white"><RefreshCw size={14} className={loading ? 'animate-spin' : ''} />Sync GitHub</button>
    </div>
    {error && <p className="mb-4 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-800">{error}</p>}
    {repos.length > 0 && <div className="grid gap-4 md:grid-cols-2">{repos.map((repo) => <div key={repo.id} className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="flex items-start justify-between"><div><a href={repo.repository_url} target="_blank" rel="noreferrer" className="text-lg font-bold hover:text-forest">{repo.name}</a><p className="mt-2 line-clamp-2 text-sm text-muted">{repo.description || 'No description'}</p></div><a href={repo.repository_url} target="_blank" rel="noreferrer" className="text-forest"><ExternalLink size={17} /></a></div>
      <div className="mt-5 flex gap-4 text-xs text-muted"><span className="flex items-center gap-1"><GitBranch size={14} />{repo.language || 'Other'}</span><span className="flex items-center gap-1"><Star size={14} />{repo.stars}</span></div>
      <div className="mt-4 border-t border-slate-100 pt-4"><label className="text-xs font-semibold">Deployment URL</label><div className="mt-2 flex gap-2"><input value={repo.deployed_url || ''} onChange={(event) => saveDeployment(repo, event.target.value)} placeholder="https://your-app.example.com" className="min-w-0 flex-1 rounded-lg bg-slate-50 px-3 py-2 text-xs outline-none" />{repo.deployed_url && <a href={repo.deployed_url} target="_blank" rel="noreferrer" className="grid h-8 w-8 place-items-center rounded-lg bg-[#e8f5ed] text-forest"><ExternalLink size={14} /></a>}</div></div>
    </div>)}</div>}
  </section>
}
