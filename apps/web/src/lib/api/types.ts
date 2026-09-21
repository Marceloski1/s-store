import type { components } from "@/lib/api/schema"

type Schemas = components["schemas"]

export type ApiSneaker = Schemas["SneakerResponse"]
export type ApiSneakerRequest = Schemas["SneakerRequest"]
export type ApiColorway = Schemas["ColorwayResponse"]
export type ApiImage = Schemas["ImageResponse"]
export type ApiGender = Schemas["Gender"]
export type ApiSneakerStatus = Schemas["SneakerStatus"]
export type ApiCatalogFacets = Schemas["CatalogFacetsResponse"]
