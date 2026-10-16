-- Steal An Egg - Clean Return To Base Hub 🛡️
local Players = game:GetService("Players")
local CoreGui = game:GetService("CoreGui")
local LocalPlayer = Players.LocalPlayer

if CoreGui:FindFirstChild("EggHubGui") then
    CoreGui.EggHubGui:Destroy()
end

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "EggHubGui"
pcall(function() ScreenGui.Parent = CoreGui end)
if not ScreenGui.Parent then ScreenGui.Parent = LocalPlayer:WaitForChild("PlayerGui") end
ScreenGui.ResetOnSpawn = false

-- النافذة الرئيسية
local MainFrame = Instance.new("Frame")
MainFrame.Parent = ScreenGui
MainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 25)
MainFrame.Position = UDim2.new(0.3, 0, 0.3, 0)
MainFrame.Size = UDim2.new(0, 260, 0, 160)
MainFrame.Active = true
MainFrame.Draggable = true

-- العنوان
local Title = Instance.new("TextLabel")
Title.Parent = MainFrame
Title.BackgroundColor3 = Color3.fromRGB(10, 10, 15)
Title.Size = UDim2.new(1, 0, 0, 40)
Title.Text = "Return To Base Hub 🛡️"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.TextSize = 16
Title.Font = Enum.Font.SourceSansBold

-- زر العودة للبداية / القاعدة
local SpawnBtn = Instance.new("TextButton")
SpawnBtn.Parent = MainFrame
SpawnBtn.BackgroundColor3 = Color3.fromRGB(50, 120, 200)
SpawnBtn.Position = UDim2.new(0.1, 0, 0.45, 0)
SpawnBtn.Size = UDim2.new(0.8, 0, 0, 50)
SpawnBtn.Text = "العودة للبداية / القاعدة 🛡️"
SpawnBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
SpawnBtn.TextSize = 15
SpawnBtn.Font = Enum.Font.SourceSansBold

-- دالة العودة النظيفة المباشرة بدون تكرار
SpawnBtn.MouseButton1Click:Connect(function()
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        local root = char.HumanoidRootPart
        
        -- 1. تصفير السرعة والحركة تماماً لتفادي الـ Rubberband
        root.AssemblyLinearVelocity = Vector3.new(0, 0, 0)
        root.AssemblyAngularVelocity = Vector3.new(0, 0, 0)
        
        -- 2. تحديد موقع الـ Spawn أو القاعدة
        local spawnPart = workspace:FindFirstChild("SpawnLocation") or workspace:FindFirstChild("Spawn")
        local targetCFrame = spawnPart and (spawnPart.CFrame + Vector3.new(0, 4, 0)) or CFrame.new(0, 12, 0)
        
        -- 3. نقل الشخصية مرة واحدة ناعمة ومباشرة
        root.CFrame = targetCFrame
        
        -- 4. تصفير السرعة مجدداً بعد النقل مباشرة لضمان الثبات
        task.wait(0.05)
        root.AssemblyLinearVelocity = Vector3.new(0, 0, 0)
    end
end)
