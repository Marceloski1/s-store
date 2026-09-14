export type NamedResource = {
  id: string
  name: string
  slug: string
}

export type NamedResourceInput = {
  name: string
  slug?: string | null
}

export type ResourcePage = {
  items: NamedResource[]
  total: number
  page: number
  size: number
  pages: number
}

export interface NamedResourceGateway {
  list(page: number, size: number): Promise<ResourcePage>
  create(input: NamedResourceInput): Promise<NamedResource>
  update(id: string, input: NamedResourceInput): Promise<NamedResource>
  remove(id: string): Promise<void>
}
