import { Router } from "express";
import {
  createShotHandler,
  deleteShotHandler,
  getShotByIdHandler,
  getShotsHandler,
  patchShotHandler,
  putShotHandler,
} from "../controllers/shots.controller.js";

const router = Router();

router.get("/", getShotsHandler);
router.get("/:id", getShotByIdHandler);
router.post("/", createShotHandler);
router.put("/:id", putShotHandler);
router.patch("/:id", patchShotHandler);
router.delete("/:id", deleteShotHandler);

export default router;