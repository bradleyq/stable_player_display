#version 150

#moj_import <minecraft:light.glsl>
#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:projection.glsl>

#if defined(ALPHA_CUTOUT) && !defined(EMISSIVE) && !defined(NO_OVERLAY) && !defined(APPLY_TEXTURE_MATRIX)
#define MAYBE_PLAYERDISP 1
#endif

#define SPLITMODEL 0

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in ivec2 UV1;
in ivec2 UV2;
in vec3 Normal;

#ifdef MAYBE_PLAYERDISP
uniform sampler2D Sampler0;
#endif
uniform sampler2D Sampler1;
uniform sampler2D Sampler2;

out float sphericalVertexDistance;
out float cylindricalVertexDistance;
out vec4 vertexColor;
out vec4 lightMapColor;
out vec4 overlayColor;
out vec2 texCoord0;
#ifdef MAYBE_PLAYERDISP
out vec2 texCoord1;
out float part;

#define SPACING 1024.0
#define MAXRANGE (0.5 * SPACING)
#define SKINRES 64
#define FACERES 8

#define SLIMCHECK0 vec2(54.0 / float(SKINRES), 20.0 / float(SKINRES))
#define SLIMCHECK1 vec2(55.0 / float(SKINRES), 20.0 / float(SKINRES))

const vec4[] subuvs = vec4[](
    vec4(4.0,  0.0,  8.0,  4.0 ), // 4x4x12
    vec4(8.0,  0.0,  12.0, 4.0 ),
    vec4(0.0,  4.0,  4.0,  16.0),
    vec4(4.0,  4.0,  8.0,  16.0),
    vec4(8.0,  4.0,  12.0, 16.0), 
    vec4(12.0, 4.0,  16.0, 16.0), 
    vec4(4.0,  0.0,  7.0,  4.0 ), // 4x3x12
    vec4(7.0,  0.0,  10.0, 4.0 ),
    vec4(0.0,  4.0,  4.0,  16.0),
    vec4(4.0,  4.0,  7.0,  16.0),
    vec4(7.0,  4.0,  11.0, 16.0), 
    vec4(11.0, 4.0,  14.0, 16.0),
    vec4(4.0,  0.0,  12.0, 4.0 ), // 4x8x12
    vec4(12.0,  0.0, 20.0, 4.0 ),
    vec4(0.0,  4.0,  4.0,  16.0),
    vec4(4.0,  4.0,  12.0, 16.0),
    vec4(12.0, 4.0,  16.0, 16.0),
    vec4(16.0, 4.0,  24.0, 16.0)
);

const vec2[] origins = vec2[](
    vec2(40.0, 16.0), // right arm
    vec2(40.0, 32.0),
    vec2(32.0, 48.0), // left arm
    vec2(48.0, 48.0),
    vec2(16.0, 16.0), // torso
    vec2(16.0, 32.0),
    vec2(0.0,  16.0), // right leg
    vec2(0.0,  32.0),
    vec2(16.0, 48.0), // left leg
    vec2(0.0,  48.0)
);

const int[] faceremap = int[](0, 0, 1, 1, 2, 3, 4, 5);
#endif

void main() {
#ifdef NO_CARDINAL_LIGHTING
    vertexColor = Color;
#else
    vertexColor = minecraft_mix_light(Light0_Direction, Light1_Direction, Normal, Color);
#endif
    lightMapColor = texelFetch(Sampler2, UV2 / 16, 0);
    overlayColor = texelFetch(Sampler1, UV1, 0);

#ifdef MAYBE_PLAYERDISP
    ivec2 dim = textureSize(Sampler0, 0);
    part = 0.0;
    texCoord1 = vec2(0.0);

    // check world projmat (not gui), 64x64 texture (player tex dim), valid fog (not hand)
    if (abs(ProjMat[2][3]) > 10e-6 && dim.x == SKINRES && dim.y == SKINRES && FogRenderDistanceEnd > FogRenderDistanceStart) {
        int partId = -int((Position.y - MAXRANGE) / SPACING);

        part = float(partId);

        if (partId != 0) {
            partId -= 1;
            vec4 samp1 = texture(Sampler0, SLIMCHECK0);
            vec4 samp2 = texture(Sampler0, SLIMCHECK1);
            bool slim = samp1.a == 0.0 || (((samp1.r + samp1.g + samp1.b) == 0.0) && ((samp2.r + samp2.g + samp2.b) == 0.0) && samp1.a == 1.0 && samp2.a == 1.0);
            int partIdMod = partId % 5;
            int outerLayer = (gl_VertexID / 24) % 2; 
            int vertexId = gl_VertexID % 4;
            int faceId = (gl_VertexID % 24) / 4;
            ivec2 faceIdTmp = ivec2(round(UV0 * SKINRES));

            // find the desired part UV origin
            vec2 UVout = origins[2 * partIdMod + outerLayer];
            vec2 UVout2 = origins[2 * partIdMod];

            // find the player head face UV origin
            if ((faceId != 1 && vertexId >= 2) || (faceId == 1 && vertexId <= 1)) {
                faceIdTmp.y -= FACERES;
            }
            if (vertexId == 0 || vertexId == 3) {
                faceIdTmp.x -= FACERES;
            }

            // calculate a faceId based on face UV origin
            faceIdTmp /= FACERES;
            faceId = (faceIdTmp.x % 4) + 4 * faceIdTmp.y;
            faceId = faceremap[faceId];
            int subuvIndex = faceId;

            if (slim && (partIdMod == 0 || partIdMod == 1)) { // select slim arms
                subuvIndex += 6;
            }
            else if (partIdMod == 2) { // select torso
                subuvIndex += 12;
            }

            vec4 subuv = subuvs[subuvIndex];
            vec2 offset = vec2(0.0);

#if SPLITMODEL == 1
            // adjust UVs in split cases
            if (faceId >= 2) {
                subuv.w -= 6.0;
                if (partId >= 5) {
                    subuv.yw += 6.0;
                }
            }
#endif

            // find the UV offset within the current part
            if (faceId == 1) {
                if (vertexId == 0) {
                    offset += subuv.zw;
                }
                else if (vertexId == 1) {
                    offset += subuv.xw;
                }
                else if (vertexId == 2) {
                    offset += subuv.xy;
                }
                else {
                    offset += subuv.zy;
                }
            }
            else {
                if (vertexId == 0) {
                    offset += subuv.zy;
                }
                else if (vertexId == 1) {
                    offset += subuv.xy;
                }
                else if (vertexId == 2) {
                    offset += subuv.xw;
                }
                else {
                    offset += subuv.zw;
                }
            }

            // apply offset to part origin and normalize
            UVout += offset;
            UVout2 += offset;
            UVout /= float(SKINRES);
            UVout2 /= float(SKINRES);

            // assign output
            vec3 wpos = Position;
            wpos.y += SPACING * (partId + 1);
            gl_Position = ProjMat * ModelViewMat * vec4(wpos, 1.0);

            sphericalVertexDistance = fog_spherical_distance(wpos);
            cylindricalVertexDistance = fog_cylindrical_distance(wpos);
            
            texCoord0 = UVout;
            texCoord1 = UVout2;

            return;
        }
    }
#endif

    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1.0);

    sphericalVertexDistance = fog_spherical_distance(Position);
    cylindricalVertexDistance = fog_cylindrical_distance(Position);

    texCoord0 = UV0;
#ifdef APPLY_TEXTURE_MATRIX
    texCoord0 = (TextureMat * vec4(UV0, 0.0, 1.0)).xy;
#endif
}
