import {
  createShot,
  findShotById,
  listShots,
  patchShot,
  removeShot,
  updateShot,
} from "../services/shots.service.js";

export async function getShotsHandler(_req, res, next) {
  try {
    const shots = await listShots();
    res.json({ ok: true, shots });
  } catch (error) {
    next(error);
  }
}

export async function getShotByIdHandler(req, res, next) {
  try {
    const shot = await findShotById(req.params.id);

    if (!shot) {
      return res.status(404).json({ ok: false, error: "Shot no encontrado" });
    }

    res.json({ ok: true, shot });
  } catch (error) {
    next(error);
  }
}

export async function createShotHandler(req, res, next) {
  try {
    const shot = await createShot(req.body ?? {});
    res.status(201).json({ ok: true, shot });
  } catch (error) {
    next(error);
  }
}

export async function putShotHandler(req, res, next) {
  try {
    const shot = await updateShot(req.params.id, req.body ?? {});

    if (!shot) {
      return res.status(404).json({ ok: false, error: "Shot no encontrado" });
    }

    res.json({ ok: true, shot });
  } catch (error) {
    next(error);
  }
}

export async function patchShotHandler(req, res, next) {
  try {
    const shot = await patchShot(req.params.id, req.body ?? {});

    if (!shot) {
      return res.status(404).json({ ok: false, error: "Shot no encontrado" });
    }

    res.json({ ok: true, shot });
  } catch (error) {
    next(error);
  }
}

export async function deleteShotHandler(req, res, next) {
  try {
    const deleted = await removeShot(req.params.id);

    if (!deleted) {
      return res.status(404).json({ ok: false, error: "Shot no encontrado" });
    }

    res.json({ ok: true });
  } catch (error) {
    next(error);
  }
}