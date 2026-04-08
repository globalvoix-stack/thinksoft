import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { db } from './db';
import { projects, projectMembers } from './schema';
import { eq, and, or } from 'drizzle-orm';

const app = express();
const PORT = 3001;

app.use(cors({ origin: true, credentials: true }));
app.use(express.json());

app.get('/api/health', async (_req, res) => {
  try {
    await db.execute('SELECT 1');
    res.json({ status: 'ok', database: 'connected' });
  } catch (err: any) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

app.get('/api/projects', async (req, res) => {
  try {
    const clerkUserId = req.headers['x-clerk-user-id'] as string;
    if (!clerkUserId) return res.status(401).json({ error: 'Unauthorized' });

    const ownedProjects = await db
      .select()
      .from(projects)
      .where(eq(projects.clerkUserId, clerkUserId));

    const memberRows = await db
      .select({ projectId: projectMembers.projectId })
      .from(projectMembers)
      .where(eq(projectMembers.clerkUserId, clerkUserId));

    const sharedIds = memberRows.map(r => r.projectId);

    let sharedProjects: typeof ownedProjects = [];
    if (sharedIds.length > 0) {
      sharedProjects = await db
        .select()
        .from(projects)
        .where(
          and(
            eq(projects.isActive, true),
          )
        );
      sharedProjects = sharedProjects.filter(p =>
        sharedIds.includes(p.id) && p.clerkUserId !== clerkUserId
      );
    }

    res.json({
      owned: ownedProjects,
      shared: sharedProjects,
    });
  } catch (err: any) {
    console.error('GET /api/projects error:', err);
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/projects', async (req, res) => {
  try {
    const clerkUserId = req.headers['x-clerk-user-id'] as string;
    if (!clerkUserId) return res.status(401).json({ error: 'Unauthorized' });

    const { title, description, imageUrl } = req.body;
    if (!title) return res.status(400).json({ error: 'title is required' });

    const [project] = await db
      .insert(projects)
      .values({ clerkUserId, title, description, imageUrl })
      .returning();

    res.status(201).json(project);
  } catch (err: any) {
    console.error('POST /api/projects error:', err);
    res.status(500).json({ error: err.message });
  }
});

app.patch('/api/projects/:id', async (req, res) => {
  try {
    const clerkUserId = req.headers['x-clerk-user-id'] as string;
    if (!clerkUserId) return res.status(401).json({ error: 'Unauthorized' });

    const id = parseInt(req.params.id);
    const { title, description, isStarred, isActive } = req.body;

    const [project] = await db
      .update(projects)
      .set({
        ...(title !== undefined && { title }),
        ...(description !== undefined && { description }),
        ...(isStarred !== undefined && { isStarred }),
        ...(isActive !== undefined && { isActive }),
        updatedAt: new Date(),
      })
      .where(and(eq(projects.id, id), eq(projects.clerkUserId, clerkUserId)))
      .returning();

    if (!project) return res.status(404).json({ error: 'Project not found' });
    res.json(project);
  } catch (err: any) {
    console.error('PATCH /api/projects/:id error:', err);
    res.status(500).json({ error: err.message });
  }
});

app.delete('/api/projects/:id', async (req, res) => {
  try {
    const clerkUserId = req.headers['x-clerk-user-id'] as string;
    if (!clerkUserId) return res.status(401).json({ error: 'Unauthorized' });

    const id = parseInt(req.params.id);
    const [deleted] = await db
      .delete(projects)
      .where(and(eq(projects.id, id), eq(projects.clerkUserId, clerkUserId)))
      .returning();

    if (!deleted) return res.status(404).json({ error: 'Project not found' });
    res.json({ success: true });
  } catch (err: any) {
    console.error('DELETE /api/projects/:id error:', err);
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`API server running on http://localhost:${PORT}`);
});
