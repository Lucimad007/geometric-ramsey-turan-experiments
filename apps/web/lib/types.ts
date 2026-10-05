export type Coord = { re: number; im: number };

export type PointRecord = {
  id: string;
  part: "W" | "Z";
  coords: Coord[];
};

export type EdgeRecord = {
  source: string;
  target: string;
  kind: "internal" | "cross";
  witness: Record<string, number>;
};

export type Statistics = Record<string, number | string | null>;

export type Experiment = {
  id: string;
  title: string;
  description: string;
  sampler: string;
  seed: number | null;
  z_seed: number | null;
  guarantees: string;
  parameters: {
    p: number;
    ell: number;
    mu: number;
    K: number;
    k: number;
  };
  points: PointRecord[];
  edges: EdgeRecord[];
  statistics: Statistics;
  notes: string[];
  cross_cloud?: {
    w: string;
    z: string;
    re: number;
    im: number;
    min_abs_im: number;
    stripe: boolean;
    arc: boolean;
    edge: boolean;
  }[];
  arc_upper?: number;
  im_threshold?: number;
};

export type IndexEntry = { id: string; title: string; file: string };
