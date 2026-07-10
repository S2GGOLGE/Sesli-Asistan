using Microsoft.AspNetCore.Mvc;

namespace Sesli_Asistan_Apı.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TestController : ControllerBase
    {
        // GET: api/test
        [HttpGet]
        public IActionResult Get()
        {
            return Ok(new { status = "ok", message = "Test API çalışıyor" });
        }

        // GET: api/test/health
        [HttpGet("health")]
        public IActionResult Health()
        {
            return Ok(new { status = "healthy" });
        }

        // POST: api/test/echo
        [HttpPost("echo")]
        public IActionResult Echo([FromBody] object payload)
        {
            return Ok(new { received = payload });
        }
    }
}
